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

# import modules
import subprocess
import json


class Command_launcher(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        
    ######################################################################################################################################
    ########################################################## SET FUNCTIONS #############################################################
    ######################################################################################################################################

    def create_asset(self, asset_name, current_entity):

        #---------------------------------------------------------------------------------------------------#
        # launch the create_asset.py script with hython in powershell                                       #
        # asset name : name of the asset to be processed, it is passed in the command line to hython        #
        # path : path of the asset to be processed, it is passed in the command line to hython              #
        # project path : path of the project, it is passed in the command line to hython                    #
        #---------------------------------------------------------------------------------------------------#

        # importe path.json to get the path of hython.exe
        with open('//gandalf/3D4-2026/Dev_Pipe/Daisy_Pipe/00_Pipeline/Plugins/Daisy_Pipe/Scripts/DaisyTools/lib/path.json', 'r') as file:
            jsonPath = json.load(file)


        project_path = self.core.projectPath
        project_path.replace("\\", "/")
        project_path.replace("//", "/")

        hython_path = jsonPath["software"]["hython"]

        # path to the create_asset.py script to be launched with hython
        python_file_path = project_path + "00_Pipeline/Plugins/Daisy_Pipe/Scripts/DaisyTools/createUSDAsset/create_asset.py"

        # path to the create_asset.py script to be launched with hython
        python_file_path = project_path + "00_Pipeline/Plugins/Daisy_Pipe/Scripts/DaisyTools/createUSDAsset/create_asset.py"

        asset_name = str(asset_name)
        to_hython_path = "cd \'" + hython_path.replace("/hython.exe", "") + "\'"

        asset_path = self.core.paths.getEntityPath(entity=current_entity)

        # create command line to launch hython with the create_asset.py script and pass the asset name and info as arguments
        command_line = f"powershell.exe \"{to_hython_path}\" ; ./hython.exe \"{python_file_path}\" --assetName \'{asset_name}\' --path '{asset_path}' --projectPath '{project_path}' "

        # launch command line in powershell
        subprocess.Popen(command_line)

