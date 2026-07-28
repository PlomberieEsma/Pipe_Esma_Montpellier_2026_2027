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
import hou, time, json
from pxr import Usd, UsdGeom
from Scripts.DaisyTools.core.core import get_core
from Scripts.DaisyTools.core.get_entity_info import get_entity_info
from Scripts.DaisyTools.template_scripts.create_toolbox import create_toolbox

print("execute template_RLO.py\n\n")

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

core = get_core()
info = get_entity_info()

usd_file_format = "usda"

shot_path = info["path"]
seq_and_sht_name = info["name"]
shot_entity = info["entity"]
shot_task = info["task"]
shot_version = core.products.getNextAvailableVersion(entity=shot_entity, product=shot_task)
project_path = core.sequencePath.replace("\\", "/")
project_path = project_path.removesuffix("/03_Production/Shots")

sequence_name = shot_entity["sequence"]
shot_name = shot_entity["shot"]

json_path = f"{project_path}/00_Pipeline/Plugins/Daisy_Pipe/Scripts/DaisyTools/lib/cameras.json"

##########################################################################################################################################
#=========================================================== SET FUNCTIONS ===============================================================
##########################################################################################################################################

def create_cam(shot_duration=24):

    new_shot = add_shot_in_json(shot_duration)
    new_shot_name = list(new_shot.keys())[0]
    new_shot_start = new_shot[new_shot_name]["start"]
    new_shot_end = new_shot[new_shot_name]["end"]

    lopnet = hou.node("/stage")
    key_cursor = hou.Keyframe()

    cam1 = lopnet.createNode("camera")
    cam1.setName(f"cam_{sequence_name}_{new_shot_name}")
    cam1.parm("primpath").set(f"/{seq_and_sht_name}/cam/cam_{sequence_name}_{new_shot_name}")

    key_cursor.setFrame(new_shot_start)
    cam1.parm("tx").setKeyframe(key_cursor)
    cam1.parm("ty").setKeyframe(key_cursor)
    cam1.parm("tz").setKeyframe(key_cursor)
    cam1.parm("rx").setKeyframe(key_cursor)
    cam1.parm("ry").setKeyframe(key_cursor)
    cam1.parm("rz").setKeyframe(key_cursor)
    
    key_cursor.setFrame(new_shot_end)
    cam1.parm("tx").setKeyframe(key_cursor)
    cam1.parm("ty").setKeyframe(key_cursor)
    cam1.parm("tz").setKeyframe(key_cursor)
    cam1.parm("rx").setKeyframe(key_cursor)
    cam1.parm("ry").setKeyframe(key_cursor)
    cam1.parm("rz").setKeyframe(key_cursor)

def add_shot_in_json(shot_duration):
    new_shot_name = None
    new_shot_start = 1001
    new_shot_end = None

    # create new shot name
    json_data = read_json(shot_duration)
    shots_in_json = json_data[sequence_name]

    if json_data["previously_empty"] == False:
        last_shot_key = list(shots_in_json.keys())[-1]
        last_shot_number = last_shot_key[-3:]
        new_shot_number = int(last_shot_number)+10
        if new_shot_number < 100:
            new_shot_name = f"sh0{new_shot_number}"
        else:
            new_shot_name = f"sh{new_shot_number}"

        # create new shot start
        end_of_last_shot = shots_in_json[last_shot_key]["end"]
        new_shot_start = end_of_last_shot + 1

        # create new shot end
        new_shot_end = new_shot_start + shot_duration

        new_shot = {new_shot_name : {
            "start": new_shot_start,
            "end": new_shot_end
            }}

        json_data[sequence_name].update(new_shot)
        write_json(json_data)
        return new_shot
    else:
        json_data["previously_empty"] = False
        write_json(json_data)
        return json_data[sequence_name]


def write_json(data):
    try:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return
    except Exception as e:
        return f"Error : {e}"


def read_json(shot_duration):
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except:
                # if the file is empty
                data = {
                    sequence_name : {
                        "sh010" : {
                            "start": 1001,
                            "end": 1001 + shot_duration,
                        }
                    },
                    "previously_empty" : True
                }
        return data
    except Exception as e:
        return f"Error : {e}"


create_cam(int(input("shot duration : ")))