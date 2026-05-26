import maya.cmds as cmds
import os, json
import PrismInit


core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_pkg_root, "lib", "usdParamsExport.json"), "r") as f:
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
        assetTask = data.get("task", "")
        fullAssetPath = os.path.join(core.assetPath, assetRelPath)
        projectName = core.projectName
        userName = core.users.getUser()

        print(f"Project : {projectName}")
        print(f"Asset   : {assetName}")
        print(f"Path    : {fullAssetPath}")
        print(f"Department: {assetDepartment}")
        print(f"Task    : {assetTask}")
        print(f"project    : {projectName}")
        print(f"Current user: {userName}")
        return {"type": "asset", "name": assetName, "path": fullAssetPath, "department": assetDepartment, "task": assetTask, "project": projectName, "user": userName}

    elif entityType == "shot":
        sequence = data.get("sequence", "")
        shot = data.get("shot", "")
        shotDepartment = data.get("department", "")
        shotTask = data.get("task", "")
        fullShotPath = os.path.join(core.shotPath, sequence, shot)
        fullShotPath = fullShotPath.replace("@", "_")
        projectName = core.projectName
        userName = core.users.getUser()
        print(f"Project  : {projectName}")
        print(f"Shot     : {sequence}_{shot}")
        print(f"Path     : {fullShotPath}")
        print(f"Department: {shotDepartment}")
        print(f"Task    : {shotTask}")
        print(f"project    : {projectName}")
        print(f"Current user: {userName}")
        return {"type": "shot", "sequence": sequence, "shot": shot, "path": fullShotPath, "department": shotDepartment, "task": shotTask, "project": projectName, "user": userName}

    else:
        print(f"Project : {projectName}")
        print("Scene is not saved inside a Prism entity.")
        return None


def export_usd(preset_name, file_path, default_prim=""):

    config = dict(usdExportParams["common"])

    if preset_name in usdExportParams["presets"]:
        config.update(usdExportParams["presets"][preset_name])
    else:
        raise ValueError(f"Preset inconnu : {preset_name}")
    
    config["file"] = file_path
    config["defaultPrim"] = default_prim
    
    cmds.mayaUSDExport(**config)

if __name__ == "__main__":
    getSavePath()
