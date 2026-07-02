from pxr.UsdUtils import fixBrokenPixarSchemas
from Scripts.DaisyTools.setupAsset import maya
from Scripts.DaisyTools.setupAsset import maya
from Scripts.DaisyTools import core
from Scripts.DaisyTools.core.dcc.launcher import get_dcc
from Scripts.DaisyTools.setupAsset.maya.setup_geo import setup_geo, geo_is_complete
import json, os

#path to the export usd parameters which are stocked in a json file
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_pkg_root, "lib", "usdParamsExport.json"), "r") as f:
    usdExportParams = json.load(f)


def get_core():
    
    #import Prism Pipeline and pcore without UI
    
    try:
        # pyrefly: ignore [missing-import]
        import PrismInit
        core = PrismInit.pcore if getattr(PrismInit, "pcore", None) else PrismInit.prismInit(prismArgs=["noUI"])
    except Exception as e:
        print(f"[Daisy] Prism est introubable. Veuillez vérifier que Prism est installé et configuré correctement. Erreur: {e}")
        return None
    return core

    #To use it import the fonction in other modules using "from Daisy_Pipe.Scripts.DaisyTools.core.core import get_core" then execute with "core = get_core()"
    #You can then use core.exampleOfPrismFonction to call prism fonction


def create_selection_set(selectedobj, set_name):
    
    #Create maya quick selection set from selected objects

    # pyrefly: ignore [missing-import]
    import maya.cmds as cmds

    if cmds.objExists(set_name) and cmds.nodeType(set_name) == "objectSet":
        cmds.delete(set_name)
        
    #If selection set already existe we delete it to recreate a new one with the same name

    set_name = cmds.sets(selectedobj, name=set_name)

    return set_name


def write_usd(preset_name, file_path, default_prim="", selection_only=True):
    
    #Write usd using mayaUsdPlugin if launched inside maya
    
    dcc = get_dcc() #get in which dcc software the code is being executed (ex: Maya, Houdini)

    if dcc == "maya": #if we are in Maya we execute this code
        # pyrefly: ignore [missing-import]
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
        config["selection"] = True

        if preset_name == "mod":

            root_exists = cmds.objExists("|" + default_prim) and cmds.nodeType("|" + default_prim) == "transform"

            if not root_exists or not geo_is_complete("|" + default_prim):
                master_grp = setup_geo(default_prim=default_prim)
                print(f"{master_grp} setup")
            else:
                master_grp = "|" + default_prim

            if selection_only:
                selection = cmds.ls(selection=True, long=True)
                if not selection:
                    raise RuntimeError(
                        "Aucune géométrie sélectionnée : sélectionne les nœuds à "
                        "exporter avant de lancer l'export USD."
                    )
            else:
                selection = cmds.select(master_grp)

            create_selection_set(selection, default_prim + "_geo")
            

        cmds.mayaUSDExport(**config)

def create_master(file_path, master_path, default_prim=""):
    
    #Create a master usd file with sublayer pointing to the lastest version of the entity usd file

    from pxr import Usd, Sdf #import Usd and Sdf library from Pxr

    if not os.path.exists(master_path): #check if master usd file already exists if not we create it

        master_stage = Usd.Stage.CreateNew(master_path) #create new master usd file
        root_layer = master_stage.GetRootLayer() #get root layer of master usd file

        root_layer.defaultPrim = default_prim #set default prim
        root_layer.startTimeCode = 1 #set start time code
        root_layer.endTimeCode = 1 #set end time code
        master_stage.SetMetadata("metersPerUnit", 0.01) #set meters per unit

        root_layer.subLayerPaths.append(file_path) #append file path to sublayer paths

        root_layer.Save()

        print(f"Fichier créé : {master_path}")

    else: #if master usd file already exists we update the sublayer paths
        layer = Sdf.Layer.FindOrOpen(master_path) #find master usd file

        layer.subLayerPaths.clear() #clear sublayer paths
        layer.subLayerPaths.append(file_path) #append file path to sublayer paths

        layer.Save() #save master usd file

        print(f"SubLayer mis à jour : {master_path}")

    
# def add_geo_variant(entity, master_path, task, entity_name, type, departement):

#     from pxr import Sdf, Usd, UsdGeom, Kind

#     core = get_core()

#     default_prim = f"/{entity_name}_asset"
#     geo_scope    = f"{default_prim}/geo"
#     proxy_path   = f"{geo_scope}/proxy"
#     render_path  = f"{geo_scope}/render"

#     productpath = os.path.join(core.getEntityPath(entity=entity), "Export", "USD", "layers", "geo.usda").replace("\\", "/")
#     print(f"productpath = {productpath}")
#     if not os.path.exists(productpath):
#         core.popup("Impossible d'exporter, veuillez executé Create USD asset avant", title="Daisy Pipeline", severity="error")
#         return

#     stage = Usd.Stage.Open(productpath)
#     root = stage.GetPrimAtPath(default_prim)

#     # S'assure que le prim racine est bien un Xform avec kind=component
#     if root.GetTypeName() != "Xform":
#         root = stage.DefinePrim(default_prim, "Xform")
#     Usd.ModelAPI(root).SetKind(Kind.Tokens.component)
#     stage.SetDefaultPrim(root)

#     if not root.GetVariantSets().HasVariantSet(departement):
#         root.GetVariantSets().AddVariantSet(departement)
#         print(f"VariantSet '{departement}' créé.")
#     else:
#         print(f"VariantSet '{departement}' existe déjà.")

#     vset = root.GetVariantSets().GetVariantSet(departement)

#     variant_exists = task in vset.GetVariantNames()

#     if not variant_exists:
#         vset.AddVariant(task)

#     vset.SetVariantSelection(task)

#     with vset.GetVariantEditContext():

#         # kind=component sur le prim racine, dans le contexte de cette variante
#         Usd.ModelAPI(root).SetKind(Kind.Tokens.component)

#         geo = stage.DefinePrim(geo_scope, "Scope")
#         UsdGeom.Imageable(geo).GetPurposeAttr().Set("default")

#         if type == "proxy":
#             if stage.GetPrimAtPath(proxy_path).IsValid():
#                 print("Le proxy existe déjà, aucune action effectuée.")
#             else:
#                 proxy = stage.DefinePrim(proxy_path, "Scope")
#                 proxy.SetMetadata("kind", "")
#                 UsdGeom.Imageable(proxy).GetPurposeAttr().Set("proxy")
#                 proxy.GetReferences().AddReference(master_path)

#             render = stage.GetPrimAtPath(render_path)
#             if render.IsValid():
#                 proxy_rel = render.GetRelationship("proxyPrim")

#                 if proxy_rel.IsValid() and proxy_rel.GetTargets() == [Sdf.Path(proxy_path)]:
#                     print("La relation proxyPrim pointe déjà correctement vers le proxy.")
#                 else:
#                     if not proxy_rel.IsValid():
#                         proxy_rel = render.CreateRelationship("proxyPrim")
#                     proxy_rel.SetTargets([Sdf.Path(proxy_path)])
#                     print("Relation proxyPrim créée/mise à jour vers :", proxy_path)

#         elif type == "render":
#             render = stage.GetPrimAtPath(render_path)

#             if render.IsValid():
#                 print("Le render existe déjà, aucune action effectuée.")
#             else:
#                 render = stage.DefinePrim(render_path, "Scope")
#                 render.SetMetadata("kind", "")
#                 UsdGeom.Imageable(render).GetPurposeAttr().Set("render")
#                 render.GetReferences().AddReference(master_path)

#             proxy_exists = stage.GetPrimAtPath(proxy_path).IsValid()
#             target_path = proxy_path if proxy_exists else render_path

#             proxy_rel = render.GetRelationship("proxyPrim")

#             if proxy_rel.IsValid() and proxy_rel.GetTargets() == [Sdf.Path(target_path)]:
#                 print("La relation proxyPrim pointe déjà correctement.")
#             else:
#                 if not proxy_rel.IsValid():
#                     proxy_rel = render.CreateRelationship("proxyPrim")
#                 proxy_rel.SetTargets([Sdf.Path(target_path)])
#                 print("Relation proxyPrim créée/mise à jour vers :", target_path)

#         else:
#             return

#     stage.GetRootLayer().Save()

def add_variant(entity, master_path, task, entity_name, type, departement):
    from pxr import Sdf, Usd, UsdGeom

    core = get_core()

    default_prim = f"/{entity_name}_asset"
    geo_scope    = f"{default_prim}/geo"
    proxy_path   = f"{geo_scope}/proxy"
    render_path  = f"{geo_scope}/render"

    productpath = os.path.join(core.getEntityPath(entity=entity), "Export", "USD", "layers", "geo.usda").replace("\\", "/")
    print(f"productpath = {productpath}")
    if not os.path.exists(productpath):
        core.popup("Impossible d'exporter, veuillez executé Create USD asset avant", title="Daisy Pipeline", severity="error")
        return

    USD_FILE    = productpath
    NEW_VARIANT = task
    PROXY_REF   = master_path
    RENDER_REF  = master_path


    stage = Usd.Stage.Open(USD_FILE)
    root  = stage.GetPrimAtPath(default_prim)

    vset = root.GetVariantSets().GetVariantSet("geo")
    vset.AddVariant(NEW_VARIANT)
    vset.SetVariantSelection(NEW_VARIANT)

    with vset.GetVariantEditContext():
        geo    = stage.DefinePrim(geo_scope, "Scope")
        UsdGeom.Imageable(geo).GetPurposeAttr().Set("default")
        if type == "proxy":
            proxy  = stage.DefinePrim(proxy_path, "Scope")
            UsdGeom.Imageable(proxy).GetPurposeAttr().Set("proxy")
            proxy.GetReferences().AddReference(PROXY_REF)
        if type == "render":
            render = stage.DefinePrim(render_path, "Scope")
            UsdGeom.Imageable(render).GetPurposeAttr().Set("render")
            render.GetReferences().AddReference(RENDER_REF)
            render.CreateRelationship("proxyPrim").SetTargets([Sdf.Path(proxy_path)])
        
        
        

    stage.GetRootLayer().Save()
    print(f"Variant '{NEW_VARIANT}' ajouté")