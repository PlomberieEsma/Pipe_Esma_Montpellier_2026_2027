from EsmaUSD.core.dcc.launcher import get_dcc
import json, os

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_pkg_root, "lib", "usdParamsExport.json"), "r") as f:
    usdExportParams = json.load(f)

def get_core():
    try:
        import PrismInit
        core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])
    except Exception as e:
        print(f"[Daisy] Prism est introubable. Veuillez vérifier que Prism est installé et configuré correctement. Erreur: {e}")
        return None
    return core


def create_selection_set(selectedobj, set_name):

    import maya.cmds as cmds

    if cmds.objExists(set_name) and cmds.nodeType(set_name) == "objectSet":
        cmds.delete(set_name)

    set_name = cmds.sets(selectedobj, name=set_name)

    return set_name


def write_usd(preset_name, file_path, default_prim="", selection_only=True, set_name=None):
    dcc = get_dcc()

    if dcc == "maya":
        import maya.cmds as cmds

        if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")

        config = dict(usdExportParams["common"])

        if preset_name in usdExportParams["presets"]:
            config.update(usdExportParams["presets"][preset_name])
        else:
            raise ValueError(f"Preset inconnu : {preset_name}")

        config["file"] = file_path
        config["defaultPrim"] = default_prim

        if selection_only:
            selection = cmds.ls(selection=True, long=True)
            if not selection:
                raise RuntimeError(
                    "Aucune géométrie sélectionnée : sélectionne les nœuds à "
                    "exporter avant de lancer l'export USD."
                )
            config["selection"] = True

            create_selection_set(selection, default_prim + "_geo")

        cmds.mayaUSDExport(**config)
