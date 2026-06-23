import os, json, re
from datetime import datetime
from EsmaUSD.core.get_entity_info import get_entity_info
from EsmaUSD.core.core import get_core, write_usd
from EsmaUSD.core.dcc.launcher import get_dcc

core = get_core()

def export_usd():
    
    info = get_entity_info()
    if info is None:
        return

    entity = info["entity"]          # dict Prism attendu par generateProductPath
    etype = entity["type"]
    dept = info["department"]
    task = info["task"]

    if etype == "asset" and dept != "mod":
        return
    if etype == "shot" and dept != "lay":
        return
    
    if not task:
        core.popup("Aucune task assignée à cette scène : impossible d'exporter l'asset/shot en USD.", title="Export USD", icon="warning")
        return

    path = core.products.generateProductPath(entity=entity, task=task, extension=".usda", version=None, location="global")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    preset = "mod" if etype == "asset" else "lay"
    write_usd(preset, path, default_prim=info["name"])
    print(f"USD exported: {path}")

    core.products.updateMasterVersion(path)

    m = re.search(r"_v(\d+)", os.path.basename(path))
    source_version = m.group(1) if m else ""

    master_path = get_master_path(path)

    write_metadata(master_path, info, preset, is_master=True, source_version=source_version)  # master
    write_metadata(path, info, preset)

def write_metadata(usd_path, info, preset,*, is_master=False, source_version=None):
    """Écrit un JSON de métadonnées à côté de l'export USD, avec exactement
    les infos utilisées par export_usd (chemin d'export réel, preset,
    default_prim, version lue dans le nom de fichier)."""

    dcc = get_dcc()
    if dcc != "maya":
        return

    import maya.cmds as cmds

    m = re.search(r"_v(\d+)", os.path.basename(usd_path))
    version = m.group(1) if m else ("master" if is_master else "")

    metadata = {
        "name": info["name"],
        "version": version,
        **({"is_master": is_master} if is_master else {}),
        **({"master_of_version": source_version} if is_master else {}),
        "preset": preset,
        "default_prim": info["name"],
        "author": info["user"],
        "comment": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "department": info["department"],
        "task": info["task"],
        "export_path": usd_path,
        "entity_path": info["path"],
        "project": info["project"],
        "project_path": info["projectPath"],
        "source_scene": cmds.file(q=True, sn=True),
    }

    json_path = os.path.join(os.path.dirname(usd_path), f"{info['name']}_metadata.json")
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved: {json_path}")

def get_master_path(versioned_path):
    parts = versioned_path.replace("\\", "/").split("/")
    # Prism structure : .../product/v0001/filename_v0001.usda
    # → .../product/master/filename_master.usda
    for i, part in enumerate(parts):
        if re.match(r"v\d+", part):
            parts[i] = "master"
            break
    filename = parts[-1]
    parts[-1] = re.sub(r"_v(\d+)", "_master", filename)
    return "/".join(parts)

export_usd()