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

print("execute layout_manager.py\n\n")

# title
try:
    from Scripts.DaisyTools.core.ascii_art import print_title
    print_title()
except:
    print("\nDaisy Pipeline\n\nby Noa Escourbanies, Leeloo Trinh-Thieu et Thomas Rubio\n\n")



class Error(Exception):
    # use to raise errors in the script
    pass

##########################################################################################################################################
#=========================================================== SET VARIABLES ===============================================================
##########################################################################################################################################

digit_number = 3 # number of digits in the seq and sht names

##########################################################################################################################################
#=========================================================== SET FUNCTIONS ===============================================================
##########################################################################################################################################

def command_check(kwargs):
    #-----------------------------------------------------------------------------------------------#
    # Check what command has been used (add, delete or clear all shots) and call the right function #
    #                                                                                               #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"                                 #
    #-----------------------------------------------------------------------------------------------#

    cameras_in_scene = hou.lopNodeTypeCategory().nodeTypes()["camera"].instances()
    cam_count_scene = 0

    # get all well named cameras in the scene
    if cameras_in_scene != ():
        cameras_in_scene = list(cameras_in_scene)
        loop_count = 0
        for camera in cameras_in_scene:
            cam_name = camera.name()
            cam_name_first_part = cam_name[:6]
            cam_name_second_part = cam_name[6+digit_number:-digit_number]

            if cam_name_first_part != "cam_sq" or cam_name_second_part != "_sh":
                del cameras_in_scene[loop_count]

            loop_count += 1

        cam_count_scene = len(cameras_in_scene)

    if int(kwargs["script_value"]) == 0:
        # if there is no shot in the HDA
        # CLEAR button
        print("clear shots")
        for camera in cameras_in_scene:
            # destroy camera node
            camera.destroy()

        # set FLO and TLO number to 0
        kwargs["node"].parm("shots_FLO").set(0)
        kwargs["node"].parm("shots_TLO").set(0)
        return

    # check the difference btw the cam number and the HDA shot number
    # to detect which function needs to be called
    count_difference = int(kwargs["script_value"]) - cam_count_scene

    if count_difference == 1:
        # new shot
        create_shot(kwargs, digit_number)
    elif count_difference == -1:
        # delete shot
        delete_shot(kwargs, cameras_in_scene)
    else:
        # issuecdetected
        issue_correction(kwargs)





def create_shot(kwargs, digit_number):
    #-----------------------------------------------------------------------------------------------#
    # Create new shot by creating a camera and naming the HDA multiParmBlock instance               #
    # modifies the FLO and TLO multiParmBlock instances too                                         #
    #                                                                                               #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"                                 #
    # digit_number = number of digits after the sequence and shot (e.g.: sq0020_sh0120 => 4 digits) #
    #-----------------------------------------------------------------------------------------------#

    from Scripts.DaisyTools.hda_scripts.create_cam import create_cam

    # get the input node for create_cam()
    nulls_in_scene = hou.lopNodeTypeCategory().nodeTypes()["null"].instances()
    null_input = None
    for null in nulls_in_scene:
        if null.name() == "cameras":
            null_input = null
            break

    # get the networkbox for create_cam()
    box_input = hou.node("/stage").findNetworkBox("/stage/camera_box")

    new_cam = create_cam(null_input, box_input, digit_number)

    # modifie the HDA
    # RLO part
    kwargs["node"].parm("sh_name"+kwargs["script_value"]).set(new_cam.name().replace("cam_", "").replace("_", " "))
    kwargs["node"].parm("cam_selection_"+kwargs["script_value"]).set(new_cam.parm("primpath"))

    # copy shot number and name from RLO to FLO and TLO
    # FLO part
    kwargs["node"].parm("shots_FLO").set(kwargs["node"].parm("shot_number").eval())
    kwargs["node"].parm("sh_name_FLO_"+kwargs["script_value"]).set(new_cam.name().replace("cam_", "").replace("_", " "))
    # TLO part
    kwargs["node"].parm("shots_TLO").set(kwargs["node"].parm("shot_number").eval())
    kwargs["node"].parm("sh_name_TLO_"+kwargs["script_value"]).set(new_cam.name().replace("cam_", "").replace("_", " "))

    print("add "+new_cam.name().replace("cam_", ""))

def delete_shot(kwargs, cameras_in_scene):
    #-------------------------------------------------------------------#
    # Delete a camera by getting the shot deleted in the multiParmBlock #
    # modifies the FLO and TLO multiParmBlock instances too             #
    #                                                                   #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"     #
    # cameras_in_scene = list of all well named cameras in the scene    #
    #-------------------------------------------------------------------#

    block = kwargs["node"]
    block_number = block.parm("shot_number").eval()

    for i in range(block_number+1):
        # loop into all shots in the HDA
        try:
            if cameras_in_scene[i].parm("primpath").eval() == block.parm(f"cam_selection_{i+1}").eval():
                # it's ok
                pass
            else:
                # the shot has been deleted
                print("del "+cameras_in_scene[i].name().replace("cam_", ""))
                # delete the corresponding camera node
                cameras_in_scene[i].destroy()

                # delete shot for FLO and TLO
                block.parm("shots_FLO").removeMultiParmInstance(i)
                block.parm("shots_TLO").removeMultiParmInstance(i)
                break

        except AttributeError as e:
            # if the user deletes the last shot
            print("del "+cameras_in_scene[i].name().replace("cam_", ""))
            cameras_in_scene[i].destroy()

            # delete shot for FLO and TLO
            block.parm("shots_FLO").removeMultiParmInstance(i)
            block.parm("shots_TLO").removeMultiParmInstance(i)
            break

def issue_correction(kwargs):
    #---------------------------------------------------------------------------#
    # In case of node deletion without deleting the shot in multiParmBlock :    #
    # delete multiParmBlock instances which have empty "cam_selection_#" field  #
    # modifies the FLO and TLO multiParmBlock instances too                     #
    #                                                                           #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"             #
    #---------------------------------------------------------------------------#

    block = kwargs["node"]
    block_number = block.parm("shot_number").eval()
    removed = False

    for i in range(block_number-1):
        # loop into all shots in the HDA
        if removed == True:
            i -= 1
            removed = False
        try:
            if block.parm(f"cam_selection_{i+1}").eval() == "":
                # if there is no camera in the camera selection field
                # remove the corresponding shot in the HDA
                block.parm("shot_number").removeMultiParmInstance(i)

                # delete shot for FLO and TLO
                block.parm("shots_FLO").removeMultiParmInstance(i)
                block.parm("shots_TLO").removeMultiParmInstance(i)
                removed = True
        except Exception as e:
            print(f"Error : {e}")

