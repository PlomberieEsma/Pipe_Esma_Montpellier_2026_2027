import os, shutil
from maya import cmds
import importlib
import EsmaUSD.core.core
importlib.reload(EsmaUSD.core.core)

if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
    cmds.loadPlugin("mayaUsdPlugin")

from EsmaUSD.core.core import getSavePath, export_usd

import PrismInit

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

        master_dir = os.path.join(saveData["path"], "Export", saveData["department"], "master")
        os.makedirs(master_dir, exist_ok=True)
        master_path = os.path.join(master_dir, f"{asset_name}_master.usda")
        shutil.copy2(usda_path, master_path)

        

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

        master_dir = os.path.join(saveData["path"], "Export", saveData["department"], "master")
        os.makedirs(master_dir, exist_ok=True)
        master_path = os.path.join(master_dir, f"{shot_name}_master.usda")
        shutil.copy2(usda_path, master_path)

saveScene()
getSavePath()