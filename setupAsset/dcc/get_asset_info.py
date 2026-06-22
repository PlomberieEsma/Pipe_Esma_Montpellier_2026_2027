import os

def get_asset_info():
    try:
        import PrismInit
        core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])
    except Exception as e:
        print(f"[Daisy] Prism est introubable. Veuillez vérifier que Prism est installé et configuré correctement. Erreur: {e}")
        return None
    
    projectName = core.projectName()
    projectPath = core.projectPath()
    
    data = core.getCurrentScenefileData()
    entityType = data.get("type", "")
    
    assetName = data.get("asset", "")
    assetRelpath = data.get("asset_path", "")
    assetDepartement = data.get("department", "")
    fullAssetPath = os.path.join(core.assetPath, assetRelpath)
    
    return {"type": "asset", "name": assetName, "path": fullAssetPath, "department": assetDepartement, "project": projectName, "projectPath": projectPath}