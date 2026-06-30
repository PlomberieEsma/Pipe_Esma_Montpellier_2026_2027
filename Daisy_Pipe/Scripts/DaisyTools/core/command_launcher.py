# import modules
import subprocess
import json
# import os
from Scripts.DaisyTools.core.core import get_core
from Scripts.DaisyTools.core.get_entity_info import get_entity_info



# importe path.json
with open('//gandalf/3D4-2026/Dev_Pipe/PrismProjPreSett/00_Pipeline/CustomModules/Python/EsmaUSD/lib/path.json', 'r') as file:
    jsonPath = json.load(file)

core = get_core()
data = core.getCurrentScenefileData()

######################################################################################################################################
########################################################## SET VARIABLES #############################################################
######################################################################################################################################

# project_path = jsonPath["global"]["project_path"]
project_path = data["project_path"]
project_path.replace("\\", "/")

hython_path = jsonPath["software"]["hython"]

# Source - https://superuser.com/a/1740297
# Posted by Keith Miller
# Retrieved 2026-05-11, License - CC BY-SA 4.0
# powershell_add_type = """Add-Type @'\nusing System;using System.Runtime.InteropServices;public class API {public enum SW : int {Hide = 0, Normal = 1, ShowMinimized = 2, Maximize = 3, ShowNoActivate = 4,Show = 5, Minimize = 6, ShowMinNoActive = 7, ShowNA = 8, Restore = 9, Showdefault = 10, Forceminimize = 11} [DllImport("user32.dll")] public static extern int ShowWindow(IntPtr hwnd, SW nCmdShow);}\n'@"""
# powershell_hide_window = "$ThisWindow = [System.Diagnostics.Process]::GetCurrentProcess().MainwindowHandle;[API]::ShowWindow($ThisWindow,'Hide');sleep -Seconds 5;[API]::ShowWindow($ThisWindow,'Show')"


# print(os.system('powershell.exe ls'))
# print(subprocess.Popen('powershell.exe ls'))

######################################################################################################################################
########################################################## SET FUNCTIONS #############################################################
######################################################################################################################################

def create_asset(asset_name):

    #---------------------------------------------------------------------------------------------------#
    # Lance le script create_asset.py avec hython dans powershell                                       #
    # asset name : nom de l'asset à traiter, il est passé par la suite dans la commande vers hython     #
    #---------------------------------------------------------------------------------------------------#


    # python_file_path = project_path + "/09_Dev/hython/create_asset.py"
    python_file_path = project_path + "/00_Pipeline/CustomModules/Python/EsmaUSD/createUSDAsset/create_asset.py"
    print(python_file_path)

    info = get_entity_info()
    print("test create asset")
    print(info)

    asset_name = str(asset_name)
    # info = str(info)
    # info.replace("'", "\\'")
    to_hython_path = "cd \'" + hython_path.replace("/hython.exe", "") + "\'"
    print(to_hython_path)
    print(info)
    path = info["path"]
    info_project_path = info["projectPath"]
    name = info["name"]
    # command_line = f"powershell.exe'{to_hython_path}' ; ./hython.exe \'{python_file_path}\' --assetName \'{asset_name}\' --info \'{info}\'"
    command_line = f"powershell.exe \"{to_hython_path}\" ; ./hython.exe \"{python_file_path}\" --assetName \'{asset_name}\' --path '{path}' --project_path '{info_project_path}' --name '{name}' "
    # command_line = f"""powershell.exe \"cd 'C:/Program Files/Side Effects Software/Houdini 20.5.445/bin'\" ; ./hython.exe '//gandalf/3D4-2026/Dev_Pipe/PrismProjPreSett/00_Pipeline/CustomModules/Python/EsmaUSD/createUSDAsset/create_asset.py' --assetName 'Bobibob' --path '{path}' --project_path '{info_project_path}' --name '{name}' """
    # command_line = f"powershell.exe \"cd 'C:/Program Files/Side Effects Software/Houdini 20.5.445/bin'\" ; New-Item 'SharedFolder' -itemType Directory "
    print(command_line)
    print(subprocess.Popen(command_line))

    # versions non fonctionnelles pour executer la commande sans ouvrir de terminal powershell
    # print(subprocess.Popen("powershell.exe " + to_hython_path + " ; ./hython.exe \'" + python_file_path + "\' --assetName '" + asset_name + "\'"), startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW, wShowWindow=subprocess.SW_HIDE))
    # subprocess.Popen("powershell.exe " + powershell_add_type + ";" + powershell_hide_window + ";" + to_hython_path + " ; ./hython.exe \'" + python_file_path + "\' --assetName '" + asset_name + "\'")
    # print(subprocess.run([to_hython_path], "./hython.exe \'" + python_file_path + "\' --assetName '" + asset_name + "\'"))

######################################################################################################################################
########################################################## CALL FUNCTIONS ############################################################
######################################################################################################################################
