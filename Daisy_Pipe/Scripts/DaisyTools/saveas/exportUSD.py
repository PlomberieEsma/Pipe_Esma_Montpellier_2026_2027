import os

from DaisyTools.core.get_entity_info import get_entity_info
from DaisyTools.core.core import get_core, write_usd, create_master, create_master_clips, SUBDIVISION_METHOD_MAP
from DaisyTools.core.dcc.launcher import get_dcc


def export_usd(params=None):

    #Export the current scene to USD, driven by the export state's settings (params).
    #params comes from EsmaUsdExportClass.getExportParams() - a plain dict, no Qt involved here.

    core = get_core()
    if core is None:
        return

    info = get_entity_info()
    if info is None:
        return

    if not info["task"]:
        core.popup("Aucune task assignée à cette scène : impossible d'exporter l'asset/shot en USD.", title="Export USD", severity="error")
        return

    entity = info["entity"]
    task = info["task"]
    name = info["name"]

    params = params or {}
    department = params.get("department") or info["department"]
    preset_name = department.split("_", 1)[-1] if "_" in department else department

    extension = params.get("extension") or ".usdc"
    default_prim = params.get("default_prim_override") or name
    whole_scene = params.get("whole_scene", False)
    nodes = params.get("nodes") or []
    update_master = params.get("update_master", True)
    update_thumbnail = params.get("update_thumbnail", True)
    export_uvs = params.get("export_uvs")
    subdivision_method = params.get("subdivision_method")
    animation_type = params.get("animation_type", "Time Samples")
    start_frame = params.get("start_frame")
    end_frame = params.get("end_frame")
    comment = params.get("comment", "")

    if not whole_scene and nodes and get_dcc() == "maya":
        # pyrefly: ignore [missing-import]
        import maya.cmds as cmds
        cmds.select(nodes, replace=True)

    overrides = {}
    if export_uvs is not None:
        overrides["exportUVs"] = export_uvs
    if subdivision_method:
        overrides["defaultMeshScheme"] = SUBDIVISION_METHOD_MAP.get(subdivision_method, subdivision_method)

    frame_range = None
    if start_frame is not None and end_frame is not None:
        frame_range = (start_frame, end_frame)

    path = core.products.generateProductPath(entity=entity, task=task, extension=extension, version=None, location="global")
    #the master is always .usda, independent of the versioned file's Outputtype:
    #it's just a thin sublayer/clip wrapper, so keeping it text-based makes it diffable
    master_path = core.products.generateProductPath(entity=entity, task=task, extension=".usda", version="master", location="global")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    is_file_per_frame = animation_type == "File per Frame" and frame_range and frame_range[0] != frame_range[1]

    if is_file_per_frame:
        base, ext = os.path.splitext(path)
        dcc = get_dcc()
        frame_paths = []
        for frame in range(int(frame_range[0]), int(frame_range[1]) + 1):
            if dcc == "maya":
                # pyrefly: ignore [missing-import]
                import maya.cmds as cmds
                cmds.currentTime(frame)
            frame_path = f"{base}.{frame:04d}{ext}"
            write_usd(preset_name, frame_path, default_prim=default_prim, selection_only=not whole_scene, overrides=overrides, frame_range=(frame, frame))
            frame_paths.append(frame_path)
        print(f"USD exported (file per frame): {len(frame_paths)} files in {os.path.dirname(path)}")
    else:
        write_usd(preset_name, path, default_prim=default_prim, selection_only=not whole_scene, overrides=overrides, frame_range=frame_range)
        print(f"USD exported: {path}")

    if update_master:
        if is_file_per_frame:
            clips_path = f"{base}.clips.usda"
            create_master_clips(frame_paths, frame_range, clips_path, default_prim=default_prim)
            create_master(clips_path, master_path, default_prim=default_prim)
        else:
            create_master(path, master_path, default_prim=default_prim)

    details = dict(entity)
    details["version"] = core.products.getProductDataFromFilepath(path).get("version", "")
    details["sourceScene"] = core.getCurrentFileName()
    details["product"] = task
    details["comment"] = comment

    info_path = core.products.getVersionInfoPathFromProductFilepath(path)
    core.saveVersionInfo(filepath=info_path, details=details)

    if update_thumbnail and core.products.getUseProductPreviews():
        preview = core.products.generateProductPreview()
        if preview:
            core.products.setProductPreview(os.path.dirname(path), preview)

    if update_master:
        master_info_path = core.products.getVersionInfoPathFromProductFilepath(master_path)
        core.saveVersionInfo(filepath=master_info_path, details=details)

    return path
