import maya.cmds as cmds
import os
import PrismInit

core = PrismInit.prismInit()

projectName = core.projectName
projectPath = core.projectPath

data = core.getCurrentScenefileData()
entityType = data.get("type", "")

def getSavePath():
    if entityType == "asset":
        assetName = data.get("asset", "")
        assetRelPath = data.get("asset_path", "")
        fullAssetPath = os.path.join(core.assetPath, assetRelPath)
        print(f"Project : {projectName}")
        print(f"Asset   : {assetName}")
        print(f"Path    : {fullAssetPath}")

    elif entityType == "shot":
        sequence = data.get("sequence", "")
        shot = data.get("shot", "")
        print(f"Project  : {projectName}")
        print(f"Shot     : {sequence}_{shot}")

    else:
        print(f"Project : {projectName}")
        print("Scene is not saved inside a Prism entity.")

getSavePath()