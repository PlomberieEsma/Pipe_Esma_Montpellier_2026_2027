import maya.cmds as cmds
import os, json
import PrismInit

core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])

with open(os.path.join(core.scriptPath, "lib", "usdParamsExport.json"), "r") as f:
    usdExportParams = json.load(f)


projectName = core.projectName
projectPath = core.projectPath

data = core.getCurrentScenefileData()
entityType = data.get("type", "")

presetExport = []


def getSavePath():
    if entityType == "asset":
        assetName = data.get("asset", "")
        assetRelPath = data.get("asset_path", "")
        assetDepartment = data.get("department", "")
        fullAssetPath = os.path.join(core.assetPath, assetRelPath)
        print(f"Project : {projectName}")
        print(f"Asset   : {assetName}")
        print(f"Path    : {fullAssetPath}")
        print(f"Department: {assetDepartment}")
        return {"type": "asset", "name": assetName, "path": fullAssetPath, "department": assetDepartment}

    elif entityType == "shot":
        sequence = data.get("sequence", "")
        shot = data.get("shot", "")
        fullShotPath = os.path.join(core.shotPath, sequence, shot)
        print(f"Project  : {projectName}")
        print(f"Shot     : {sequence}_{shot}")
        print(f"Path     : {fullShotPath}")
        return {"type": "shot", "sequence": sequence, "shot": shot, "path": fullShotPath}

    else:
        print(f"Project : {projectName}")
        print("Scene is not saved inside a Prism entity.")
        return None


def export_usd(preset_name,file_path, default_prim=""):

    config = dict(usdExportParams["common"])

    if preset_name in usdExportParams["presets"]:
        config.update(usdExportParams["presets"][preset_name])
    else:
        raise ValueError(f"Preset inconnu : {preset_name}")
    
    cmds.usdExport(**config)

if __name__ == "__main__":
    getSavePath()
