import os, importlib
from EsmaUSD.core.get_entity_info import get_entity_info
from EsmaUSD.core.core import get_core, write_usd, create_master
import EsmaUSD.core.core
importlib.reload(EsmaUSD.core.core)

core = get_core()

def export_usd():
    
    info = get_entity_info()
    if info is None:
        return

    entity = info["entity"]          # dict Prism attendu par generateProductPath
    etype = entity["type"]
    dept = info["department"]
    task = info["task"]

    if not task:
        core.popup("Aucune task assignée à cette scène : impossible d'exporter l'asset/shot en USD.", title="Export USD", severity="error")
        return

    path = core.products.generateProductPath(entity=entity, task=task, extension=".usda", version=None, location="global")
    master_Path = core.products.generateProductPath(entity=entity, task=task, extension=".usda", version="master", location="global")

    if etype == "asset" and dept == "mod":
        write_usd("mod", path, default_prim=info["name"], selection_only=True)
        create_master(path, master_Path, default_prim=info["name"])


    else:
        return
    
    if etype == "shot":
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"USD exported: {path}")

    comment = "coucou"

    scene = core.getCurrentFileName()
    details = core.getScenefileData(scene)
    details.pop("filename", None)
    details.pop("extension", None)
    details["version"] = core.products.getProductDataFromFilepath(path).get("version", "")
    details["sourceScene"] = scene
    details["product"] = task
    details["comment"] = comment

    info_path = core.products.getVersionInfoPathFromProductFilepath(path)
    core.saveVersionInfo(filepath=info_path, details=details)
    
    master_info_path = core.products.getVersionInfoPathFromProductFilepath(master_Path)
    core.saveVersionInfo(filepath=master_info_path, details=details)

export_usd()