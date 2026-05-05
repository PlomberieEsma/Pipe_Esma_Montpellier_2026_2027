# TO DO :
# - checker la modL ET la modH
# - renommer les nodes qui ne le sont pas déjà (je sais pas si c'est indispensable, à voir)

import hou, os, json

# importe path.json
with open('C:/Users/3D4/Downloads/04_usd/TEST_USD_PROJECT/08_Dev/path.json', 'r') as file:
    jsonPath = json.load(file)

#=========================================================================================================================================
#=========================================================== SET VARIABLES ===============================================================
#=========================================================================================================================================

project_path = jsonPath["global"]["project_path"]
assets = os.listdir(project_path + "/03_Production/Assets")

asset_name = "table"
tasks = os.listdir(project_path + "/03_Production/Assets/" + asset_name + "/Export")
usd_file_format = "usda"

string_to_detect = "ModH"
is_variant = False


previews_deleted = False
contrecompte = 0
for i in range(len(tasks)):
    if previews_deleted:
        contrecompte += 1
        previews_deleted = False
    if string_to_detect not in tasks[i-contrecompte]:
        tasks.pop(i-contrecompte)
        previews_deleted = True
    else:
        tasks[i-contrecompte] = tasks[i-contrecompte].replace(string_to_detect, asset_name)

variants = tasks
# tasks = os.listdir(project_path + "/03_Production/Assets/" + asset_name + "/Export")

variant_index = 0
for variant in variants:
    if "_var" in variant:
        is_variant = True
    else:
        variants[variant_index] = variant + "_var1"
    variant_index += 1


compGeo_nodes = {}
restructSceneGraph_nodes = {}


#=========================================================================================================================================
#============================================================== HOUDINI ==================================================================
#=========================================================================================================================================

lopnet = hou.node("/stage")


for variant in variants:
    # component geometry
    compGeo_nodes.update({variant : lopnet.createNode("componentgeometry")})
    compGeo_nodes[variant].setName("in_" + variant)
    compGeo_nodes[variant].parm("sourceinput").set(3)
    compGeo_nodes[variant].parm("sourceusdref").set(project_path + "/03_Production/Assets/" + asset_name + "/Export/ModH" + variant.replace("_var1", "").replace(asset_name, "") + "/master/" + asset_name + "_ModH" + variant.replace("_var1", "").replace(asset_name, "") + "_master." + usd_file_format)
    compGeo_nodes[variant].parm("sourceproxyusdref").set(project_path + "/03_Production/Assets/" + asset_name + "/Export/ModL" + variant.replace("_var1", "").replace(asset_name, "") + "/master/" + asset_name + "_ModL" + variant.replace("_var1", "").replace(asset_name, "") + "_master." + usd_file_format)
    compGeo_nodes[variant].parm("sourcesimproxyusdref").set(project_path + "/03_Production/Assets/" + asset_name + "/Export/ModL" + variant.replace("_var1", "").replace(asset_name, "") + "/master/" + asset_name + "_ModL" + variant.replace("_var1", "").replace(asset_name, "") + "_master." + usd_file_format)


    # restructure scene graph to delete sim proxy
    restructSceneGraph_nodes.update({variant : lopnet.createNode("restructurescenegraph")})
    restructSceneGraph_nodes[variant].setName("del_sim_proxy_" + variant)
    restructSceneGraph_nodes[variant].parm("primpattern").set("/ASSET/geo/sim_proxy")
    restructSceneGraph_nodes[variant].parm("op").set(2)
    restructSceneGraph_nodes[variant].setInput(0, compGeo_nodes[variant])


# material library
matLib_node = lopnet.createNode("materiallibrary")
matLib_node.parm("matpathprefix").set("/ASSET/mtl/")

# component geometry variants
if is_variant:
    compGeoVar_node = lopnet.createNode("componentgeometryvariants")
    compGeoVar_node.parm("variantnamesrc").set(1)
    compGeoVar_node.parm("variantname").set("variant_`@input`")

    variant_number = 0
    for node in compGeo_nodes:
        # print(node +" "+str(variant_number))
        compGeoVar_node.setInput(variant_number, restructSceneGraph_nodes[node])
        variant_number += 1


# component material
compMat_node = lopnet.createNode("componentmaterial")
compMat_node.setInput(1, matLib_node)
if is_variant:
    compMat_node.setInput(0, compGeoVar_node)
else:
    for node in compGeo_nodes:
        compMat_node.setInput(0, restructSceneGraph_nodes[node])


# component output
compOutput_node = lopnet.createNode("componentoutput")
compOutput_node.setInput(0, compMat_node)
compOutput_node.parm("rootprim").set("/" + asset_name)
# compOutput_node.parm("filename").set("" + asset_name + "`." + usd_file_format)
compOutput_node.parm("filename").set(asset_name + "." + usd_file_format)
# compOutput_node.parm("lopoutput").set(project_path + "/04_USD/asset/\`chs(\"name\")\`/\`chs(\"filename\")\`")
compOutput_node.parm("lopoutput").set(project_path + "/04_USD/asset/" + asset_name + "/" + asset_name + "." + usd_file_format)
compOutput_node.parm("payloadlayer").set("payload." + usd_file_format)
compOutput_node.parm("geolayer").set("geo." + usd_file_format)
compOutput_node.parm("mtllayer").set("mtl." + usd_file_format)
compOutput_node.parm("extralayer").set("extra." + usd_file_format)

compOutput_node.parm("execute").pressButton()