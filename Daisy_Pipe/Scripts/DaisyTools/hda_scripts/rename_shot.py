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
import qtpy.QtWidgets as qt
import qtpy.QtCore as qc
import qtpy.QtGui as qg
from Scripts.DaisyTools.core.core import get_core

print("execute rename_shot.py\n\n")

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

class PaddedSpinBox(qt.QSpinBox):
    #-----------------------------------------------------------------------------------#
    # Create a custom Qt SpinBox to keep the potential leading 0 before the shot number #
    #                                                                                   #
    # return the object                                                                 #
    #-----------------------------------------------------------------------------------#
    def __init__(self, parent=None, digits=3):
        super().__init__(parent)
        self._digits = digits

    def textFromValue(self, value):
        # Format integer with leading zeros (e.g., 001, 042)
        return f"{value:0{self._digits}d}"

def button_action(kwargs, new_shot_name):
    #-----------------------------------------------------------------------------------#
    # Set and applies the new values for the shot name                                  #
    # (the HDA shot name, the camera primpath, the HDA camera path and the camera name) #
    #                                                                                   #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"                     #
    # new_shot_name = number set in the window                                          #
    #-----------------------------------------------------------------------------------#

    new_shot_name = f"{new_shot_name:0{digit_number}d}"

    #-------------------------------- set new values ---------------------------------#
    node = kwargs["node"]
    camera_path = node.parm("cam_selection_"+kwargs["script_multiparm_index"])
    camera_path_content = camera_path.eval()

    splited_camera_path = camera_path_content.split("/")
    camera_name = splited_camera_path[-1]

    sq_and_sh_name = camera_name.replace("cam_", "").replace("_", " ")

    new_camera_name = camera_name.replace(camera_name[-digit_number:], new_shot_name)
    new_camera_path = camera_path_content.replace(camera_name, new_camera_name)
    new_sq_and_sh_name = sq_and_sh_name.replace(sq_and_sh_name[-digit_number:], new_shot_name)

    #-------------------------------- apply new values ---------------------------------#
    # apply to shot name in the HDA
    node.parm("sh_name"+kwargs["script_multiparm_index"]).set(new_sq_and_sh_name)

    # get all well named cameras in the scene
    cameras_in_scene = hou.lopNodeTypeCategory().nodeTypes()["camera"].instances()
    if cameras_in_scene != ():
        cameras_in_scene = list(cameras_in_scene)
        loop_count = 0
        for camera in cameras_in_scene:
            if camera.parm("primpath").eval() == camera_path_content:

                # apply to camera name
                camera.setName(new_camera_name)

            loop_count += 1

    # apply to camera selection in the HDA and camera primpath
    camera_path.set(new_camera_path)

    print(f"rename shot : \n{sq_and_sh_name} to\n{new_sq_and_sh_name}")

def renaming_window(kwargs, current_shot_name):
    #-----------------------------------------------------------------------#
    # Create the GUI window to help the user to set the new shot name       #
    #                                                                       #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"         #
    # current_shot_name = current shot name comming from the HDA shot name  #
    #                                                                       #
    # return the window                                                     #
    #-----------------------------------------------------------------------#

    current_shot_number = int(current_shot_name[-digit_number:])

    #-------------------------------- create window ---------------------------------#
    # get existing QApplication instance to prevent crashes
    app = qt.QApplication.instance()
    if app is None:
        qt.QApplication([])

    # create the widget window
    window = qt.QWidget()
    window.setWindowTitle("shot rename")
    window.resize(200, 100)

    # change window icon
    core = get_core()
    project_path = core.sequencePath.replace("\\", "/")
    project_path = project_path.removesuffix("/03_Production/Shots")
    window.setWindowIcon(qg.QIcon(f"{project_path}/00_Pipeline/Plugins/Daisy_Pipe/Integration/ui/daisy_logo.png"))

    # parent the houdini's main Qt window to ensure the window stays open and managed by houdini
    main_window = hou.ui.mainQtWindow()
    window.setParent(main_window, qc.Qt.Window)

    #-------------------------------- create elements ---------------------------------#
    layout = qt.QGridLayout(window)

    # label title
    # label_title = qt.QLabel()
    # label_title.setText("Rename shot")
    # label_title.setStyleSheet("""
    # font-size: 20px;
    # margin-bottom: 20px;
    # """)
    # layout.addWidget(label_title, 0, 0, 1, 2)

    # label
    label = qt.QLabel()
    label.setText(current_shot_name.replace(current_shot_name[-digit_number:], ""))
    label.setStyleSheet("""
    font-size: 20px;
    """)
    label.setAlignment(qc.Qt.AlignRight | qc.Qt.AlignVCenter)
    layout.addWidget(label, 0, 0)

    # spin box
    spin_box = PaddedSpinBox(digits = digit_number)
    spin_box.setStyleSheet("""
    font-size: 20px;
    """)
    spin_box.setMinimum(1)
    spin_box.setMaximum((10**digit_number)-1)
    spin_box.setValue(current_shot_number)
    layout.addWidget(spin_box, 0, 1)

    # button
    button = qt.QPushButton("Apply")
    button.setStyleSheet("""
    font-size: 20px;
    """)
    button.clicked.connect(lambda : button_action(
        kwargs,
        spin_box.value()
    ))
    layout.addWidget(button, 1, 0, 1, 2)

    return window

def rename_shot(kwargs):
    #-------------------------------------------------------------------------------------------#
    # Launch the window creation to rename the selected shot and place it next to the cursor    #
    #                                                                                           #
    # kwargs = dict taken from the HDA multiParmBlock "shot_number"                             #
    #-------------------------------------------------------------------------------------------#

    current_shot_name = kwargs["node"].parm("sh_name"+kwargs["script_multiparm_index"]).eval()

    window = renaming_window(
        kwargs,
        current_shot_name = current_shot_name
        )

    # move to mouse cursor
    cursor_position = qg.QCursor.pos()
    window.move(
        cursor_position.x()-(window.width()*0.75),
        cursor_position.y()+30
        )

    # show window
    window.show()
