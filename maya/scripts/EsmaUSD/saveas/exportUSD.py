from datetime import datetime
import json, os, shutil, importlib, EsmaUSD.core.core
from maya import cmds
importlib.reload(EsmaUSD.core.core)

from EsmaUSD.core.core import getSavePath, export_usd

import PrismInit

if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
    cmds.loadPlugin("mayaUsdPlugin")

core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])


def saveScene():
    saveData = getSavePath()
    if saveData is None:
        return

    if saveData["type"] == "asset" and saveData["department"] == "mod":

        asset_name = saveData["name"]

        version = 1
        while True:
            version_dir = os.path.join(saveData["path"], "Export", f"layer_{saveData['department']}", f"v{version:04d}")
            if not os.path.exists(version_dir):
                break
            version += 1

        os.makedirs(version_dir, exist_ok=True)

        usda_path = os.path.join(version_dir, f"{asset_name}_v{version:04d}.usda")

        export_usd("mod", usda_path, default_prim=asset_name)
        print(f"USD exported: {usda_path}")

        master_dir = os.path.join(saveData["path"], "Export", f"layer_{saveData['department']}", "master")
        os.makedirs(master_dir, exist_ok=True)
        master_path = os.path.join(master_dir, f"{asset_name}_master.usda")
        shutil.copy2(usda_path, master_path)

        # Version metadata
        json_version = usda_path.replace(".usda", "_metadata.json")
        write_metadata(json_version, version, saveData)

        # Master metadata
        json_master = master_path.replace(".usda", "_metadata.json")
        write_metadata(json_master, "master", saveData)       

    elif saveData["type"] == "shot" and saveData["department"] != "lay":
        shot_name = f"{saveData['sequence']}_{saveData['shot']}"
        version = 1
        while True:
            version_dir = os.path.join(saveData["path"], "Export", f"layer_{saveData['department']}", f"v{version:04d}")
            if not os.path.exists(version_dir):
                break
            version += 1

        os.makedirs(version_dir, exist_ok=True)

        usda_path = os.path.join(version_dir, f"{shot_name}_v{version:04d}.usda")
        export_usd("shot", usda_path, default_prim=shot_name)
        print(f"USD exported: {usda_path}")

        master_dir = os.path.join(saveData["path"], "Export", f"layer_{saveData['department']}", "master")
        os.makedirs(master_dir, exist_ok=True)
        master_path = os.path.join(master_dir, f"{shot_name}_master.usda")
        shutil.copy2(usda_path, master_path)

def write_metadata(json_path, version, saveData):
    metadata = {
        "version": version,
        "author": saveData["user"],
        "comment": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "department": saveData["department"],
        "task": saveData["task"],
        "path": saveData["path"],
        "project": saveData["project"],
        "project_path": core.projectPath,
        "source_scene": cmds.file(q=True, sn=True),
    }
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved: {json_path}")

saveScene()