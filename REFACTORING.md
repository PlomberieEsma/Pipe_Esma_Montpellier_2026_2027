# Refactoring — EsmaUSD & setupAsset

Plan d'action pour supprimer les doublons entre les deux outils, remplacer le
hard-code par l'API Prism, et brancher les exports sur les **products** Prism.

Ordre conseillé : **§1 → §2 → §3 → §4**. Les §1/§2 corrigent aussi des bugs
réels (cf. §5).

---

## 1. Unifier la récupération de l'entité (supprime un gros doublon)

### Problème
`getSavePath()` (`maya/scripts/EsmaUSD/core/core.py`) et `get_asset_info()`
(`setupAsset/dcc/get_asset_info.py`) font la **même chose** : init du core,
`getCurrentScenefileData()`, reconstruction d'un dict d'entité. Le boilerplate
d'init du core est en plus copié 3 fois.

### À faire
Créer **un seul** module partagé qui expose `get_core()` + `get_entity_info()`,
et faire importer les deux outils depuis là.

### Exemple — `setupAsset/dcc/prism_context.py` (nouveau fichier)

```python
import os


def get_core():
    """Retourne l'instance Prism core, qu'on soit dans un DCC ou en standalone."""
    import PrismInit
    if getattr(PrismInit, "pcore", None):
        return PrismInit.pcore
    return PrismInit.prismInit(prismArgs=["noUI"])


def get_entity_info():
    """
    Dict d'entité normalisé pour la scène courante, valable asset ET shot.
    Renvoie None si la scène n'est pas dans une entité Prism.

    Les clés type/asset_path/sequence/shot sont celles attendues par
    l'API Prism (core.products, core.paths). On garde aussi des champs
    pratiques (name, path, project) pour l'affichage.
    """
    core = get_core()
    data = core.getCurrentScenefileData()
    entityType = data.get("type", "")

    if entityType not in ("asset", "shot"):
        print("La scène n'est pas dans une entité Prism.")
        return None

    # entity dict "pur" Prism (à passer tel quel à core.products / core.paths)
    if entityType == "asset":
        entity = {"type": "asset", "asset_path": data.get("asset_path", "")}
        name = data.get("asset", "")
    else:
        entity = {"type": "shot",
                  "sequence": data.get("sequence", ""),
                  "shot": data.get("shot", "")}
        name = f"{data.get('sequence', '')}_{data.get('shot', '')}"

    # Prism connaît déjà le chemin disque de l'entité : ne pas le reconstruire
    path = core.paths.getEntityPath(entity=entity)

    return {
        "entity": entity,                       # <-- à donner à l'API Prism
        "name": name,
        "path": path,
        "department": data.get("department", ""),
        "task": data.get("task", ""),
        "project": core.projectName,            # PROPRIÉTÉ, pas une fonction
        "projectPath": core.projectPath,
        "user": core.username,
    }
```

> ⚠️ `core.projectName` / `core.projectPath` sont des **propriétés** (sans
> parenthèses). `get_asset_info.py` les appelle aujourd'hui comme des fonctions
> → bug (cf. §5).

### Ensuite
- `core/core.py` : supprimer `getSavePath()` et importer `get_entity_info`.
- `get_asset_info.py` : remplacer son contenu par un appel à `get_entity_info`
  (ou supprimer le fichier et adapter les imports).

---

## 2. Remplacer le hard-code de chemins/versions par l'API products

### Problème
Dans `saveas/exportUSD.py`, le template `Export/layer_<dept>/vNNNN/`, la boucle
`while True` de versioning et la copie `shutil.copy2` vers `master/` sont écrits
**à la main et en double** (une fois pour l'asset, une fois pour le shot).

### À faire
Utiliser `core.products` qui implémente déjà ce layout depuis le template du
projet. Un seul bloc fonctionne alors pour asset **et** shot.

### Exemple — nouveau `saveScene()`

```python
import os
from setupAsset.dcc.prism_context import get_core, get_entity_info
from EsmaUSD.core.core import export_usd


def saveScene():
    info = get_entity_info()
    if info is None:
        return

    # Règles métier (à garder explicites)
    dept = info["department"]
    if info["entity"]["type"] == "asset" and dept != "mod":
        return
    if info["entity"]["type"] == "shot" and dept == "lay":
        return

    core = get_core()
    entity = info["entity"]
    task = info["task"] or dept       # ta task d'export

    # 1. Prism calcule le chemin de la PROCHAINE version selon le template projet
    path = core.products.generateProductPath(
        entity=entity,
        task=task,
        extension=".usda",
        version=None,                 # None => prochaine version dispo
        location="global",
    )

    # 2. Export USD à ce chemin
    os.makedirs(os.path.dirname(path), exist_ok=True)
    preset = "mod" if entity["type"] == "asset" else "shot"
    export_usd(preset, path, default_prim=info["name"])
    print(f"USD exported: {path}")

    # 3. Master géré par Prism (plus de shutil.copy2)
    core.products.updateMasterVersion(path)
```

### Tableau de correspondance hard-code → API Prism

| Hard-code actuel (`exportUSD.py`) | Remplacer par |
|---|---|
| `os.path.join(path, "Export", f"layer_{dept}", f"v{version:04d}")` | `core.products.generateProductPath(entity, task, extension=".usda")` |
| boucle `while True: version += 1` | géré par `generateProductPath(version=None)` ou `core.products.getNextAvailableVersion(entity, product)` |
| `shutil.copy2(usda_path, master_path)` | `core.products.updateMasterVersion(path)` |
| `os.path.join(core.assetPath, assetRelPath)` | `core.paths.getEntityPath(entity=entity)` |
| `os.path.join(core.shotPath, seq, shot)` + `.replace("@","_")` | `core.paths.getEntityPath(entity=entity)` |

---

## 3. Comment fonctionnent les *products* Prism (référence)

Un **product** = un output versionné rattaché à une entité, sous une task.
C'est exactement ton `Export/<dept>/<task>/vNNNN + master`, mais généré par
Prism depuis le template projet. Logique dans `PrismUtils/Products.py`.

```
Entité (asset/shot)
 └─ Task ("mod")
     └─ Product ("ours_polaire")
         ├─ v0001/ ours_polaire_v0001.usda
         ├─ v0002/ ours_polaire_v0002.usda
         └─ master/ ours_polaire.usda   ← pointe vers la dernière version
```

### Méthodes clés (signatures réelles)

```python
# Génère le chemin versionné (version=None => prochaine dispo)
core.products.generateProductPath(entity, task, extension=None, version=None,
                                  location="global", returnDetails=False)

# Numéro de la prochaine version libre
core.products.getNextAvailableVersion(entity, product)

# Relire la dernière version (utile pour l'import/référence dans setupAsset)
core.products.getLatestVersionpathFromProduct(product, entity=None, includeMaster=True)

# Lister toutes les versions
core.products.getVersionsFromProduct(entity, product, locations="all")

# Créer / mettre à jour le master
core.products.updateMasterVersion(path)
```

### Lire le chemin d'export pour un import (côté setupAsset)

```python
core = get_core()
entity = {"type": "asset", "asset_path": "chars/ours_polaire"}
latest = core.products.getLatestVersionpathFromProduct(
    "ours_polaire", entity=entity, includeMaster=True
)
# latest -> chemin du .usda master à référencer / importer
```

### `returnDetails=True` pour le metadata

```python
details = core.products.generateProductPath(
    entity=entity, task=task, extension=".usda",
    version=None, returnDetails=True,
)
# details : dict avec version, dossier, etc. -> à réutiliser dans le metadata
```

---

## 4. Metadata : s'aligner sur Prism plutôt que du JSON maison

### Problème
`write_metadata()` écrit un `<name>_metadata.json` à la main, et lit des clés
(`saveData["user"]`, `["task"]`, `["project"]`) que `getSavePath()` ne fournit
jamais → `KeyError` (cf. §5).

### Options (par ordre de préférence)
1. **Attacher le metadata au product Prism** via `setTaskData`, pour que la
   donnée vive dans le projet et soit relisible par d'autres outils :
   ```python
   core.entities.setTaskData(entity, department, task, "comment", "")
   core.entities.setTaskData(entity, department, task, "lastExport", path)
   ```
2. Si tu tiens au JSON sidecar, le construire depuis `get_entity_info()` (qui
   fournit `user`, `task`, `project`) + `returnDetails` pour la version, pour
   qu'il n'y ait plus de clé manquante.

### Exemple JSON corrigé

```python
def write_metadata(json_path, version, info, source_scene):
    metadata = {
        "version": version,
        "author": info["user"],
        "comment": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "department": info["department"],
        "task": info["task"],
        "path": info["path"],
        "project": info["project"],
        "project_path": info["projectPath"],
        "source_scene": source_scene,   # cmds.file(q=True, sn=True) passé en argument
    }
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)
```

---

## 5. Bugs à corriger (en faisant les §1–§4)

| # | Fichier | Bug | Correction |
|---|---|---|---|
| 1 | `get_asset_info.py:11-12` | `core.projectName()` / `core.projectPath()` appelés comme fonctions → `TypeError` | propriétés : `core.projectName`, `core.projectPath` |
| 2 | `exportUSD.py:75,79,81` | `write_metadata` lit `saveData["user"/"task"/"project"]` jamais fournis par `getSavePath()` → `KeyError` | passer le dict unifié `get_entity_info()` (§1) |
| 3 | `dpt_choose_menu.py:13` | `parent=maya_main_window()` : symbole non défini, et évalué à la définition de classe | `def __init__(self, parent=None):` puis `parent = parent or get_main_window()` |
| 4 | `core/core.py:16-17` | `data`/`entityType` calculés à l'import du module → figés | les calculer **dans** la fonction à chaque appel (résolu par `get_entity_info()`) |

### Exemple correction bug #3 — `dpt_choose_menu.py`

```python
from setupAsset.dcc.launcher import get_qt, get_main_window

QtWidgets, QtCore, QtGui = get_qt()


class AssetSetupWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        if parent is None:
            parent = get_main_window()
        super(AssetSetupWindow, self).__init__(parent)
        ...
```

---

## 6. Checklist

- [ ] Créer `setupAsset/dcc/prism_context.py` (`get_core` + `get_entity_info`) — §1
- [ ] `core/core.py` : retirer `getSavePath()` + le boilerplate core, importer le module partagé — §1
- [ ] `get_asset_info.py` : déléguer à `get_entity_info()` (ou supprimer) + fix `projectName`/`projectPath` — §1, bug #1
- [ ] `exportUSD.py` : réécrire `saveScene()` sur `core.products` (un seul bloc asset+shot) — §2
- [ ] `exportUSD.py` : supprimer la boucle `while True`, le template manuel et `shutil.copy2` — §2
- [ ] Metadata : `setTaskData` ou JSON corrigé via le dict unifié — §4, bug #2
- [ ] `dpt_choose_menu.py` : fix `maya_main_window()` → `get_main_window()` — bug #3
- [ ] Tester un export asset (`mod`) et un export shot, vérifier `vNNNN/` + `master/`
```
