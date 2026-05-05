# import modules
import subprocess
import json
# import os

# importe path.json
with open('C:/Users/3D4/Downloads/04_usd/TEST_USD_PROJECT/08_Dev/path.json', 'r') as file:
    jsonPath = json.load(file)

######################################################################################################################################
########################################################## SET VARIABLES #############################################################
######################################################################################################################################

project_path = jsonPath["global"]["project_path"]
hython_path = jsonPath["software"]["hython"]

# print(os.system('powershell.exe ls'))
# print(subprocess.Popen('powershell.exe ls'))

######################################################################################################################################
########################################################## SET FUNCTIONS #############################################################
######################################################################################################################################

def create_asset(asset_name):
    # lance le script create_asset.py avec hython dans powershell
    # asset name : nom de l'asset à traiter, il est passé par la suite dans la commande  vers hython
    python_file_path = project_path + "/08_dev/hython/create_asset.py"


    asset_name = str(asset_name)
    to_hython_path = "cd \'" + hython_path.replace("/hython.exe", "") + "\'"
    print(subprocess.Popen("powershell.exe " + to_hython_path + " ; ./hython.exe \'" + python_file_path + "\' --assetName '" + asset_name + "\'"))

######################################################################################################################################
########################################################## CALL FUNCTIONS ############################################################
######################################################################################################################################

# create_asset("table")