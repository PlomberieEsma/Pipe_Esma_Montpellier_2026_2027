def template_shading():

    #-------------------------------------------------------------------------------#
    # This function creates the houdini node template for the Shading department    #
    # return the list of all nodes in a dictionary                                  #
    #-------------------------------------------------------------------------------#

    #----------------------------------- imports -----------------------------------#
    import hou

    from Scripts.DaisyTools.core.core import get_core
    from Scripts.DaisyTools.core.get_entity_info import get_entity_info


    #-------------------------------- set variables --------------------------------#
    usd_file_format = "usda"
    
    core = get_core()
    info = get_entity_info()

    asset_path = info["path"]
    asset_name = info["name"]
    asset_entity = info["entity"]
    asset_task = info["task"]
    asset_version = core.products.getNextAvailableVersion(entity=asset_entity, product=asset_task)
    import_path = f"{asset_path}/Export/USD/master/{asset_name}_USD_master.{usd_file_format}"
    path_til_task = core.products.getProductPathFromEntity(entity=asset_entity, includeProduct=False)
    export_path = f"{path_til_task}\\{asset_task}\\{asset_version}\\{asset_name}_{asset_task}_{asset_version}.{usd_file_format}"
    node_position = [0,0]


    #-------------------------------- create nodes ---------------------------------#
    lopnet=hou.node("/stage")

    ref_geo1 = lopnet.createNode("reference")
    ref_geo1.setName("ref_geo1")
    ref_geo1.setPosition(node_position)
    ref_geo1.parm("enable").set(0) #disable multi-input
    ref_geo1.parm("primpath1").set("/`pythonexprs(\"__import__('pxr').Sdf.Layer.FindOrOpen(hou.pwd().evalParm('filepath1')).defaultPrim\")`") #re1ferenced file's default primitive
    ref_geo1.parm("filepath1").set(import_path)
    ref_geo1.parm("filerefprim1").set("") #reference specific primitive
    ref_geo1.parm("filerefprimpath1").set("`chs(\"primpath1\")`")

    set_variant1 = lopnet.createNode("setvariant")
    set_variant1.setName("set_variant1")
    set_variant1.setInput(0, ref_geo1)
    node_position[1] -= 1
    set_variant1.move(node_position)
    set_variant1.parm("num_variants").set(2)
    set_variant1.parm("variantset1").set("geo")
    set_variant1.parm("variantname1").set("geo_var_01")
    set_variant1.parm("variantset2").set("grm")
    set_variant1.parm("variantname2").set("grm_var_01")

    layer_break1 = lopnet.createNode("layerbreak")
    layer_break1.setName("layer_break1")
    layer_break1.setInput(0, set_variant1)
    node_position[1] -= 1
    layer_break1.move(node_position)

    scale_down1 = lopnet.createNode("xform")
    scale_down1.setName("scale_down1")
    scale_down1.setInput(0, layer_break1)
    node_position[1] -= 1
    scale_down1.move(node_position)
    scale_down1.parm("scale").set(0.01)

    create_component1 = lopnet.createNode("primitive")
    create_component1.setName("create_component1")
    create_component1.setInput(0, scale_down1)
    node_position[1] -= 1
    create_component1.move(node_position)
    create_component1.parm("primpath").set("/`lopinputprims('.', 0)`")
    create_component1.parm("primkind").set("component") #component

    create_mtl1 = lopnet.createNode("primitive")
    create_mtl1.setName("create_mtl1")
    create_mtl1.setInput(0, scale_down1)
    node_position[1] -= 1
    create_mtl1.move(node_position)
    create_mtl1.parm("primpath").set("/`chs(\"../create_component1/primpath\")`/mtl")
    create_mtl1.parm("parentprimtype").set("UsdGeomScope") #scope
    create_mtl1.parm("primtype").set("UsdGeomScope") #scope

    create_shader1 = lopnet.createNode("materiallibrary")
    create_shader1.setName("create_shader1")
    create_shader1.setInput(0, create_mtl1)
    node_position[1] -= 5
    create_shader1.move(node_position)
    create_shader1.parm("matpathprefix").set("/`chs(\"../create_component1/primpath\")`/mtl/")

    configure_mtl_primitives1 = lopnet.createNode("configureprimitive")
    configure_mtl_primitives1.setName("configure_mtl_primitives1")
    configure_mtl_primitives1.setInput(0, create_mtl1)
    node_position[1] -= 2
    configure_mtl_primitives1.move(node_position)
    configure_mtl_primitives1.setColor(hou.Color((0.3,0.3,0.3)))
    configure_mtl_primitives1.parm("primpattern").set("/`chs(\"../create_component1/primpath\")`/mtl/*")
    configure_mtl_primitives1.parm("settype").set(1)
    configure_mtl_primitives1.parm("type").set("UsdShadeMaterial") #material
    configure_mtl_primitives1.parm("setspecifier").set(1)

    assign_shader1 = lopnet.createNode("assignmaterial")
    assign_shader1.setName("assign_shader1")
    assign_shader1.setInput(0, configure_mtl_primitives1)
    node_position[1] -= 2
    assign_shader1.move(node_position)

    scale_up1 = lopnet.createNode("xform")
    scale_up1.setName("scale_up1")
    scale_up1.setInput(0, assign_shader1)
    node_position[1] -= 5
    scale_up1.move(node_position)
    scale_up1.parm("primpattern").set("`chs(\"../create_component1/primpath\")`")
    scale_up1.parm("scale").set(100)

    config_mtl_layer1 = lopnet.createNode("configurelayer")
    config_mtl_layer1.setName("config_mtl_layer1")
    config_mtl_layer1.setInput(0, scale_up1)
    node_position[1] -= 1
    config_mtl_layer1.move(node_position)
    config_mtl_layer1.parm("setsavepath").set(1)
    config_mtl_layer1.parm("savepath").set(export_path)
    config_mtl_layer1.parm("setdefaultprim").set(1)
    config_mtl_layer1.parm("defaultprim").set("/`chs(\"../create_component1/primpath\")`")

    usd_rop1 = lopnet.createNode("usd_rop")
    usd_rop1.setName("usd_rop1")
    usd_rop1.setInput(0, config_mtl_layer1)
    node_position[1] -= 1
    usd_rop1.move(node_position)
    usd_rop1.parm("lopoutput").set("")
    usd_rop1.parm("postrender").set("$PRISMJOB/00_Pipeline/Plugins/Daisy_Pipe/Scripts/DaisyTools/saveas/create_version_info.py")
    usd_rop1.parm("lpostrender").set("python")

    output = {"ref_geo1" : ref_geo1,
              "set_variant1" : set_variant1,
              "layer_break1" : layer_break1,
              "scale_down1" : scale_down1,
              "create_component1" : create_component1,
              "create_mtl1" : create_mtl1,
              "create_shader1" : create_shader1,
              "configure_mtl_primitives1" : configure_mtl_primitives1,
              "assign_shader1" : assign_shader1,
              "scale_up1" : scale_up1,
              "config_mtl_layer1" : config_mtl_layer1,
              "usd_rop1" : usd_rop1}
    return output



template_shading()