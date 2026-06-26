from EsmaUSD.core.dcc.launcher import get_dcc
import json, os

#path to the export usd parameters which are stocked in a json file
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_pkg_root, "lib", "usdParamsExport.json"), "r") as f:
    usdExportParams = json.load(f)


def get_core():
    
    #import Prism Pipeline and pcore without UI
    
    try:
        import PrismInit
        core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])
    except Exception as e:
        print(f"[Daisy] Prism est introubable. Veuillez vérifier que Prism est installé et configuré correctement. Erreur: {e}")
        return None
    return core

    #To use it import the fonction in other modules using "from EsmaUSD.core.core import get_core" then execute with "core = get_core()"
    #You can then use core.exampleOfPrismFonction to call prism fonction


def create_selection_set(selectedobj, set_name):
    
    #Create maya quick selection set from selected objects

    import maya.cmds as cmds

    if cmds.objExists(set_name) and cmds.nodeType(set_name) == "objectSet":
        cmds.delete(set_name)
        
    #If selection set already existe we delete it to recreate a new one with the same name

    set_name = cmds.sets(selectedobj, name=set_name)

    return set_name


def write_usd(preset_name, file_path, default_prim="", selection_only=True, set_name=None):
    
    #Write usd using mayaUsdPlugin if launched inside maya
    
    dcc = get_dcc() #get in which dcc software the code is being executed (ex: Maya, Houdini)

    if dcc == "maya": #if we are in Maya we execute this code
        import maya.cmds as cmds

        if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")
            
            #check if mayaUsdPlugin is loaded, if not we load it

        config = dict(usdExportParams["common"]) #get default export parameters from json file

        if preset_name in usdExportParams["presets"]:
            config.update(usdExportParams["presets"][preset_name])
        else:
            raise ValueError(f"Preset inconnu : {preset_name}")

        config["file"] = file_path
        config["defaultPrim"] = default_prim

        if selection_only: #check if maya nodes are being selected before writing USD file, if none are selected, cancel the operation
            selection = cmds.ls(selection=True, long=True)
            if not selection:
                raise RuntimeError(
                    "Aucune géométrie sélectionnée : sélectionne les nœuds à "
                    "exporter avant de lancer l'export USD."
                )
            config["selection"] = True

            create_selection_set(selection, default_prim + "_geo")

        cmds.mayaUSDExport(**config)
