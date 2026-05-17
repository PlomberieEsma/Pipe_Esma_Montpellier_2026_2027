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


def export_usd(file_path, default_prim="", **overrides):

    params = dict(
        # -- Output file --------------------------------------------------
        file=file_path,
        append=False,
        defaultUSDFormat="usda",            # usdc | usda
        # -- Root / prim --------------------------------------------------
        defaultPrim=default_prim,
        rootPrim="",
        rootPrimType="scope",               # scope | xform | ...
        # -- Geometry -----------------------------------------------------
        exportUVs=False,
        exportSkels="none",                 # none | auto
        exportSkin="none",                  # none | auto | explicit
        exportBlendShapes=False,
        exportDisplayColor=False,
        exportColorSets=False,
        exportComponentTags=False,
        defaultMeshScheme="catmullClark",   # catmullClark | none | loop | bilinear
        normalizeNurbs=False,
        preserveUVSetNames=False,
        geomSidedness="derived",            # derived | single | double
        referenceObjectMode="none",         # none | default | defaultWithRename

        # -- Animation ----------------------------------------------------
        frameRange=(cmds.currentTime(q=True), cmds.currentTime(q=True)),
        frameStride=1.0,
        frameSample=[0.0],
        animationType="timesamples",        # timesamples | curves | curvesAndSamples
        eulerFilter=False,
        staticSingleSample=False,
        # -- Materials ----------------------------------------------------
        exportMaterials=False,
        exportAssignedMaterials=False,
        shadingMode="useRegistry",          # useRegistry | displayColor | none
        convertMaterialsTo=["UsdPreviewSurface"],
        exportMaterialCollections=False,
        exportCollectionBasedBindings=False,
        materialCollectionsPath="",
        materialsScopeName="Looks",
        legacyMaterialScope=False,
        exportRelativeTextures="automatic", # automatic | absolute | relative
        # -- Instances / references ---------------------------------------
        exportInstances=False,
        exportRefsAsInstanceable=False,
        exportStagesAsRefs=False,
        hideSourceData=False,
        # -- Visibility / transforms --------------------------------------
        exportVisibility=False,
        mergeTransformAndShape=False,
        includeEmptyTransforms=False,
        stripNamespaces=False,
        worldspace=False,
        # -- Cameras / lights ---------------------------------------------
        defaultCameras=False,
        # -- Selection / filtering ----------------------------------------
        selection=False,
        renderableOnly=False,
        # filterTypes=["typeName"],         # exclude Maya node types
        # exportRoots=["|path|to|root"],    # export specific DAG subtrees
        renderLayerMode="defaultLayer",     # defaultLayer | currentLayer | modelingVariant
        # -- Kinds --------------------------------------------------------
        kind="",                            # component | assembly | group | subcomponent
        disableModelKindProcessor=False,
        # -- Units / axis -------------------------------------------------
        upAxis="mayaPrefs",                 # mayaPrefs | y | z
        unit="mayaPrefs",
        metersPerUnit=0.0,
        exportDistanceUnit=False,
        # -- Schemas / chasers / job contexts -----------------------------
        # apiSchema=["MyAPI"],              # extra API schemas to apply
        # jobContext=["Arnold"],            # render-delegate job contexts
        # chaser=["myChaser"],              # export chasers
        # chaserArgs=[["chaser","key","value"]],
        compatibility="",                   # appleArKit | ...
        # -- Metadata -----------------------------------------------------
        # customLayerData=[["key","string","value"]],
        writeDefaults=False,
        # -- Callbacks ----------------------------------------------------
        melPerFrameCallback="",
        melPostCallback="",
        pythonPerFrameCallback="",
        pythonPostCallback="",
        # -- Misc ---------------------------------------------------------
        ignoreWarnings=False,
        verbose=False,
    )

    params.update(overrides)
    cmds.usdExport(**params)

if __name__ == "__main__":
    getSavePath()
