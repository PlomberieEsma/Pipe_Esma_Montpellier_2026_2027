import maya.cmds as cmds
import os
import PrismInit

core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])

projectName = core.projectName
projectPath = core.projectPath

data = core.getCurrentScenefileData()
entityType = data.get("type", "")


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


def asset_export_usd_mod(file_path, default_prim=""):
    cmds.mayaUSDExport(
        file=file_path,
        exportUVs=True,
        exportSkels="none",
        exportSkin="none",
        exportBlendShapes=False,
        exportDisplayColor=False,
        exportColorSets=True,
        exportComponentTags=True,
        exportAssignedMaterials=False,
        exportMaterials=False,
        defaultMeshScheme="catmullClark",
        defaultUSDFormat="usda",
        rootPrimType="scope",
        defaultPrim=default_prim,
        exportInstances=True,
        exportVisibility=True,
        mergeTransformAndShape=True,
        includeEmptyTransforms=True,
        stripNamespaces=False,
        worldspace=False,
        exportStagesAsRefs=True,
        upAxis="mayaPrefs",
        unit="mayaPrefs",
        legacyMaterialScope=False,
    )


def saveScene():
    saveData = getSavePath()
    if saveData is None:
        return

    if saveData["type"] == "asset" and saveData["department"] == "mod":
        asset_name = saveData["name"]
        usda_path = os.path.join(saveData["path"], f"{asset_name}.usda")
        asset_export_usd_mod(usda_path, default_prim=asset_name)
        print(f"USD exported: {usda_path}")

    elif saveData["type"] == "shot":
        shot_name = f"{saveData['sequence']}_{saveData['shot']}"
        usda_path = os.path.join(saveData["path"], f"{shot_name}.usda")
        asset_export_usd_mod(usda_path, default_prim=shot_name)
        print(f"USD exported: {usda_path}")

if __name__ == "__main__":
    getSavePath()
    saveScene()
