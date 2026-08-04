#                           .=     ,        =.
#                   _  _   /'/    )\,/,/(_   \ \
#                    `//-.|  (  ,\\)\//\)\/_  ) |
#                    //___\   `\\\/\\/\/\\///'  /
#                 ,-"~`-._ `"--'_   `"'"`  _ \`'"~-,_
#                 \       `-.  '_`.      .'_` \ ,-"~`/
#                  `.__.-'`/  ( -\        /- )|-.__,'
#                    ||   |    \ O)  /^\ (O / |
#                    `\\  |         /   `\    /
#                      \\  \       /      `\ /
#                       `\\ `-.  /' .---.--.\
#                         `\\/`~(, '()      ('
#                          /(O) \\   _,.-.,_)
#                         //  \\ `\'`      /
#                        / |  ||   `""'"~"`
#                      /'  |__||
#                            `o
#      ___       _                    _          ___               
#     / _ \___ _(_)__ __ __     ___  (_)__  ___ / (_)__  ___       
#    / // / _ `/ (_-</ // /    / _ \/ / _ \/ -_) / / _ \/ -_)      
#   /____/\_,_/_/___/\_, /    / .__/_/ .__/\__/_/_/_//_/\__/       
#                   /___/    /_/    /_/                            
#
#   by Noa Escourbanies, Leeloo Trinh-Thieu and Thomas Rubio
#   art by Joan G. Stark (Spunk)

#import modules
import hou

print("execute create_cam.py\n\n")

# title
try:
    from Scripts.DaisyTools.core.ascii_art import print_title
    print_title()
except:
    print("\nDaisy Pipeline\n\nby Noa Escourbanies, Leeloo Trinh-Thieu et Thomas Rubio\n\n")



class Error(Exception):
    # use to raise errors in the script
    pass


def command_check(kwargs):
    cameras_in_scene = hou.lopNodeTypeCategory().nodeTypes()["camera"].instances()
    digit_number = 3 # number of digits in the seq and sht names
    cam_count_scene = 0

    if cameras_in_scene != ():
        cameras_in_scene = list(cameras_in_scene)
        # print(cameras_in_scene)
        loop_count = 0
        for camera in cameras_in_scene:
            cam_name = camera.name()
            cam_name_first_part = cam_name[:6]
            cam_name_second_part = cam_name[6+digit_number:-digit_number]

            if cam_name_first_part != "cam_sq" or cam_name_second_part != "_sh":
                # print("delete "+str(camera))
                del cameras_in_scene[loop_count]

            loop_count += 1

        cam_count_scene = len(cameras_in_scene)
    #     print(f"cam_count_scene : {cam_count_scene}")
    #     print("kwargs : "+kwargs["script_value"])
    # print(cameras_in_scene)

    if int(kwargs["script_value"]) == 0:
        print("clear shots")
        for camera in cameras_in_scene:
            camera.destroy()
        return

    count_difference = int(kwargs["script_value"]) - cam_count_scene

    if count_difference == 1:
        # print("new shot")
        create_shot(kwargs, digit_number)
    elif count_difference == -1:
        # print("delete shot")
        delete_shot(kwargs, cameras_in_scene)
    else:
        print("there is a problem")
        error_correct(kwargs, cameras_in_scene, digit_number)





def create_shot(kwargs, digit_number):
    from Scripts.DaisyTools.template_scripts.create_cam import create_cam
    
    nulls_in_scene = hou.lopNodeTypeCategory().nodeTypes()["null"].instances()
    null_input = None
    for null in nulls_in_scene:
        if null.name() == "cameras":
            null_input = null
            break

    box_input = hou.node("/stage").findNetworkBox("/stage/camera_box")

    new_cam = create_cam(null_input, box_input, digit_number)

    kwargs["node"].parm("sh_name"+kwargs["script_value"]).set(new_cam.name().replace("cam_", "").replace("_", " "))
    kwargs["node"].parm("cam_selection_"+kwargs["script_value"]).set(new_cam.parm("primpath"))

    print("add "+new_cam.name().replace("cam_", ""))

def delete_shot(kwargs, cameras_in_scene):
    block = kwargs["node"]
    block_number = block.parm("shot_number").eval()

    for i in range(block_number+1):
        # print(i+1)
        try:
            # print(cameras_in_scene[i].parm("primpath").eval())
            # print(block.parm(f"cam_selection_{i+1}").eval())
            if cameras_in_scene[i].parm("primpath").eval() == block.parm(f"cam_selection_{i+1}").eval():
                pass
            else:
                print("del "+cameras_in_scene[i].name().replace("cam_", ""))
                cameras_in_scene[i].destroy()
                break
        except AttributeError as e:
            print("del "+cameras_in_scene[i].name().replace("cam_", ""))
            cameras_in_scene[i].destroy()
            break

def error_correct(kwargs, cameras_in_scene, digit_number):
    block = kwargs["node"]
    block_number = block.parm("shot_number").eval()
    removed = False

    for i in range(block_number-1):
        if removed == True:
            i -= 1
            removed = False
        # print(i+1)
        try:
            # print(block.parm(f"cam_selection_{i+1}").eval())
            if block.parm(f"cam_selection_{i+1}").eval() == "":
                block.parm("shot_number").removeMultiParmInstance(i)
                removed = True
        except Exception as e:
            print(f"Error : {e}")