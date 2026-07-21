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
#   by Noa Escourbanies, Leeloo Trinh-Thieu et Thomas Rubio
#   art by Joan G. Stark (Spunk)

name = "CustomExportSettings"
classname = "CustomExportSettings"

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from functools import partial

import os, sys

from DaisyTools.core.command_launcher import Command_launcher
from DaisyTools.core.asset_browser import AssetBrowserUI
from DaisyTools.ui.maya_state_manager import EsmaUsdExportClass

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Daisy_Pipe_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        if self.isMaya():
            self.mayastate = EsmaUsdExportClass()

        if self.isStandalone():
            self.importUsdPackages()

        self.Command_launcher = Command_launcher(core, plugin)
        self.AssetBrowserUI = AssetBrowserUI(core, plugin)
        self.core.registerCallback("onProjectBrowserStartup", self.onProjectBrowserStartup, plugin=self)
        self.core.registerCallback("openPBAssetContextMenu", self.openPBAssetContextMenu, plugin=self)
        self.core.registerCallback("openPBAssetTaskContextMenu", self.openPBAssetTaskContextMenu, plugin=self)
        self.core.registerCallback("openPBShotTaskContextMenu", self.openPBShotTaskContextMenu, plugin=self)
        self.core.registerCallback("openPBFileContextMenu", self.openPBFileContextMenu, plugin=self)

        if self.isMaya():
            self.core.registerCallback("onStateManagerOpen", self.onStateManagerOpen, plugin=self)

    def onStateManagerOpen(self, origin):
        import importlib
        from DaisyTools.ui import maya_state_manager
        importlib.reload(maya_state_manager)
        origin.loadState(maya_state_manager.EsmaUsdExportClass)

        menu = QMenu(origin.b_createExport)
        menu.addAction("Export", lambda: origin.createState("Export", setActive=True))
        menu.addAction("EsmaUsdExport", lambda: origin.createState("EsmaUsdExport", setActive=True))
        origin.b_createExport.setMenu(menu)

        # TOP GENERAL Menu
    def onProjectBrowserStartup(self, origin):
        
        #-----------------------------------------------------------------------------------#
        # Create a general menu 'DaisyMenu'                                                 #
        # Create an option 'Asset Browser'                                                  #
        # Launch the opening of the Asset Browser when 'Asset Browser' is triggered         #
        #-----------------------------------------------------------------------------------#

        origin.daisyMenu = QMenu("DaisyMenu")
        # onAssetBrowserAction = QAction( "Asset Browser", origin)
        # onAssetBrowserAction.triggered.connect(lambda: self.onAssetBrowser(origin))
        # origin.daisyMenu.addAction(onAssetBrowserAction)
        origin.menubar.addMenu(origin.daisyMenu)

    ##############################################################################################################
    ###########################     SHOT TASK Contextual Menu - Asset Browser     ################################
    ##############################################################################################################

    def openPBFileContextMenu (self, origin, rcMenu, widget):
        #-----------------------------------------------------------------------------------#
        # Create an option "Asset Browser" on the context menu in shots' files              #
        # Only for SetDress and RLO Tasks                                                   #
        # When clicked, launch the Asset Browser UI with the task as argument               #
        #-----------------------------------------------------------------------------------#
        
        entity = origin.getCurrentEntity()
        widgetType = "department" if widget == origin.lw_departments else "task"

        if entity or entity["type"] in ["shot", "sequence"] and widgetType == "task":
            
            # Check the department
            deptItem = origin.lw_departments.currentItem()
            if not deptItem:
                return
            department = deptItem.data(Qt.UserRole)

            # Check existing tasks and their names
            existingTasks = self.core.entities.getCategories(entity, step=department)

            if "SetDress" in existingTasks:
                task = "SetDress"
            elif "RLO" in existingTasks:
                task = "RLO"
            else:
                return

            openAssetBrowserAction = QAction("Houdini Layout Scene", origin)
            openAssetBrowserAction.triggered.connect(
                lambda: self.onAssetBrowser(origin, task=task)
            )

            # Recherche du sous-menu "Create new version from preset"
            presetMenu = None
            for act in rcMenu.actions():
                if act.menu() and act.text() == self.core.tr("Create new version from preset"):
                    presetMenu = act.menu()
                    break

            if presetMenu:
                presetMenu.addAction(openAssetBrowserAction)
            else:
                # fallback si le sous-menu n'existe pas (ex: pas de presets configurés)
                rcMenu.addAction(openAssetBrowserAction) 

    def openPBShotTaskContextMenu(self, origin, rcMenu, widget):
    
        #-----------------------------------------------------------------------------------#
        # Create an option "Asset Browser" on the context menu in shots' files              #
        # Only for SetDress and RLO Tasks                                                   #
        # When clicked, launch the Asset Browser UI with the task as argument               #
        #-----------------------------------------------------------------------------------#
        
        entity = origin.getCurrentEntity()
        widgetType = "department" if widget == origin.lw_departments else "task"

        if entity or entity["type"] in ["shot", "sequence"] and widgetType == "task":
            
            # Check the department
            deptItem = origin.lw_departments.currentItem()
            if not deptItem:
                return
            department = deptItem.data(Qt.UserRole)

            # Check existing tasks and their names
            existingTasks = self.core.entities.getCategories(entity, step=department)

            if "SetDress" in existingTasks:
                openAssetBrowserAction = QAction("AssetBrowser", origin)
                openAssetBrowserAction.triggered.connect(lambda: self.onAssetBrowser(origin, task="SetDress"))
                rcMenu.addAction(openAssetBrowserAction)
            elif "RLO" in existingTasks:
                openAssetBrowserAction = QAction("AssetBrowser", origin)
                openAssetBrowserAction.triggered.connect(lambda: self.onAssetBrowser(origin, task="RLO"))
                rcMenu.addAction(openAssetBrowserAction)
            else:
                return      

    def onAssetBrowser(self, origin, task=None):
        
        #-----------------------------------------------------------------------------------#
        # Get the selected asset from the Create USD Asset option                           #
        # Launch the create asset function from Toto's script                               #
        #-----------------------------------------------------------------------------------#

        self.AssetBrowserUI.onAssetBrowserTriggered(origin, task)


    ##############################################################################################################
    ###########################     ASSET Contextual Menu - Create USD      ######################################
    ##############################################################################################################

    def openPBAssetContextMenu(self, origin, rcMenu, asset):
        
        #-----------------------------------------------------------------------------------#
        # Add an option "CreateUSD Asset" to the context menu for assets                    #
        # When clicked, launch the function onCreateUsdAsset with the asset as argument     #
        #-----------------------------------------------------------------------------------#
        
        # Asset is a PySide6.QtCore.QModelIndex
        # Get the item
        item = asset.data(Qt.UserRole)
        if item is None:
            return
        # self.core.popup("Item: %s" % item)

        # Check if the item is an asset
        if item["type"] != "asset":
            return
        
        # Create an action named "Create USD Asset" and add it to the context menu
        createUsdAssetAction = QAction( "Create USD Asset", origin)
        createUsdAssetAction.triggered.connect(lambda: self.onCreateUsdAsset(item))
        rcMenu.addAction(createUsdAssetAction)

    def onCreateUsdAsset(self, item):
        
        #-----------------------------------------------------------------------------------#
        # Get the selected asset from the Create USD Asset option                           #
        # Launch the create asset function from Toto's script                               #
        #-----------------------------------------------------------------------------------#

        self.core.popup("Create USD for asset: %s" % item["asset"])
        self.Command_launcher.create_asset(item["asset"], item)


    ##############################################################################################################
    ###########################     ASSET TASK Contextual Menu - Variant     #####################################
    ##############################################################################################################

    def openPBAssetTaskContextMenu(self, origin, rcMenu, widget):
        
        #-----------------------------------------------------------------------------------#
        # Create a submenu "Add Variants" to the context menu for assets' task              #
        # Add as options every current existing task                                        #
        # When clicked, launch the function onCreateVariant with the task as argument       #
        #-----------------------------------------------------------------------------------#
        
        # Asset is a PySide6.QtCore.QModelIndex
        # Check where the cursor is to launch at the right spot
        entity = origin.getCurrentEntity()
        widgetType = "department" if widget == origin.lw_departments else "task"

        if entity or entity["type"] in ["asset"] and widgetType == "task":
            # Check the department
            deptItem = origin.lw_departments.currentItem()
            if not deptItem:
                return
            department = deptItem.data(Qt.UserRole)

            # Check existing tasks and their names
            existingTasks = self.core.entities.getCategories(entity, step=department)
            existingBaseTasks = [t for t in existingTasks if not any(c.isdigit() for c in t)]
            # CHECK - self.core.popup("Tasks trouvées: %s" % existingBaseTasks)

            # Create the contextual menu and actions
            addVarMenu = QMenu("Add Variants", origin)

            if not existingBaseTasks:
                emptyAction = QAction("No existing tasks", addVarMenu)
                emptyAction.setEnabled(False)
                addVarMenu.addAction(emptyAction)
            else:
                for taskName in existingBaseTasks:
                    taskAction = QAction("Add Variant : %s" % taskName, addVarMenu)
                    taskAction.triggered.connect(partial(self.onCreateVariant, origin, entity, department, taskName, existingTasks))
                    addVarMenu.addAction(taskAction)

            rcMenu.addMenu(addVarMenu)

    def onCreateVariant(self, origin, entity, department, taskName, existingTasks):
        
        #-----------------------------------------------------------------------------------#
        # Get the chosen task from the Create Variant option                                #
        # Create the task with the same name and variant increment                          #
        #-----------------------------------------------------------------------------------#
        
        # Check existing tasks and determine the right name
        if f"{taskName}_02" not in existingTasks:
            varTaskName = f"{taskName}_var02"
        else:
            varTaskName = None
            for i in range(3, 99):
                candidate = f"{taskName}_var{i:02d}"
                if candidate not in existingTasks:
                    varTaskName = candidate
                    break

            if varTaskName is None:
                self.core.popup("Impossible de trouver un nom de variante disponible pour %s" % taskName)
                return
        
        path = self.core.entities.createCategory(entity, department, varTaskName)
        if not path:
            return
        origin.refreshTasks()
        return path







    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    







    def importUsdPackages(self):

        try:
            extModPath = os.path.join(self.pluginDirectory, "ExternalModules")
            extModPath = extModPath.replace("\\", "/")

            os.environ["PATH"] += os.pathsep + extModPath + "/USD/bin"
            os.environ["PATH"] += os.pathsep + extModPath + "/USD/lib"
            os.environ["PYTHONPATH"] = extModPath + "/USD/lib/python"
            os.environ["PYTHONPATH"] += extModPath + "/USD/bin"

            sys.path.append(extModPath)
            sys.path.insert(0, extModPath + "/USD/lib/python")
            sys.path.insert(0, extModPath + "/USD/lib/python/pxr")


        except Exception as e:
            self.console.showMessageBoxError("USD packages could not be imported", str(e))

        try:
            from pxr import Usd, UsdGeom, Sdf, Gf, Kind, UsdShade, UsdSkel, Vt, Tf, Ar
            print("Successfully imported USD packages")
        except Exception as e:
            print("USD packages could not be imported", str(e))
            return

    def isMaya(self):

        return self.core.appPlugin.pluginName == "Maya"
    
    def isStandalone(self):

        return self.core.appPlugin.pluginName == "Standalone"

    def isHoudini(self):

        return self.core.appPlugin.pluginName == "Houdni"
