import hou

def command_check(kwargs):
    cameras_in_scene = hou.lopNodeTypeCategory().nodeTypes()["camera"].instances()
    digit_number = 3 # number of digits in the seq and sht names
    cam_count_scene = 0

    if cameras_in_scene != ():
        cameras_in_scene = list(cameras_in_scene)
        print(cameras_in_scene)
        loop_count = 0
        for camera in cameras_in_scene:
            cam_name = camera.name()
            cam_name_first_part = cam_name[:6]
            cam_name_second_part = cam_name[6+digit_number:-digit_number]

            if cam_name_first_part != "cam_sq" or cam_name_second_part != "_sh":
                print("delete "+str(camera))
                del cameras_in_scene[loop_count]

            loop_count += 1

        cam_count_scene = len(cameras_in_scene)
        print(f"cam_count_scene : {cam_count_scene}")
        print("kwargs : "+kwargs["script_value"])
    print(cameras_in_scene)

    count_difference = int(kwargs["script_value"]) - cam_count_scene

    if count_difference == 1:
        print("new shot")
        create_new_shot(kwargs)
    elif count_difference == -1:
        print("delete shot")
        delete_shot(kwargs)
    else:
        print("there is a problem")
        error_correct(kwargs)





def create_new_shot(kwargs):
    if kwargs["script_value"] != '0':

        from Scripts.DaisyTools.template_scripts.create_cam import create_cam
        
        nulls_in_scene = hou.lopNodeTypeCategory().nodeTypes()["null"].instances()
        null_input = None
        for null in nulls_in_scene:
            if null.name() == "cameras":
                null_input = null
                break

        box_input = hou.node("/stage").findNetworkBox("/stage/camera_box")

        new_cam = create_cam(null_input, box_input)

        kwargs["node"].parm("sh_name"+kwargs["script_value"]).set(new_cam.name().replace("cam_", "").replace("_", " "))
        kwargs["node"].parm("cam_selection_"+kwargs["script_value"]).set(new_cam.parm("primpath"))

def delete_shot(kwargs):
    pass

def error_correct(kwargs):
    block = kwargs["node"]
    block_number = block.parm("shot_number").eval()
    removed = False

    for i in range(block_number-1):
        if removed == True:
            i -= 1
            removed = False
        print(i+1)
        try:
            print(block.parm(f"cam_selection_{i+1}").eval())
            if block.parm(f"cam_selection_{i+1}").eval() == "":
                block.parm("shot_number").removeMultiParmInstance(i)
                removed = True
        except Exception as e:
            print(f"Error : {e}")