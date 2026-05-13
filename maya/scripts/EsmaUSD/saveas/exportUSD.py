import os
from maya import cmds
from EsmaUSD.core.core import getSavePath, export_usd

import PrismInit

core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])

def saveScene():
    saveData = getSavePath()
    if saveData is None:
        return

    if saveData["type"] == "asset" and saveData["department"] == "mod":
        asset_name = saveData["name"]
        usda_path = os.path.join(saveData["path"], f"{asset_name}.usda")
        export_usd(usda_path, default_prim=asset_name)
        print(f"USD exported: {usda_path}")

    elif saveData["type"] == "shot":
        shot_name = f"{saveData['sequence']}_{saveData['shot']}"
        usda_path = os.path.join(saveData["path"], f"{shot_name}.usda")
        export_usd(usda_path, default_prim=shot_name)
        print(f"USD exported: {usda_path}")

getSavePath()