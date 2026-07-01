

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt
from functools import partial

import os, sys

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Daisy_Pipe_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        if self.isStandalone():
            self.importUsdPackages()

        self.core.registerCallback("openPBAssetContextMenu", self.onOpenPBAssetContextMenu, plugin=self)
        self.core.registerCallback("openPBAssetTaskContextMenu", self.onOpenPBAssetTaskContextMenu, plugin=self)

        self.core.registerCallback("onStateStartup", self.onStateStartup, plugin=self, priority=40)
        self.core.registerCallback("onStateGetSettings", self.onStateGetSettings, plugin=self)
        self.core.registerCallback("onStateSettingsLoaded", self.onStateSettingsLoaded, plugin=self)
        self.core.registerCallback("preExport", self.preExport, plugin=self)
        self.core.registerCallback("postExport", self.postExport, plugin=self)

    def onOpenPBAssetContextMenu(self, origin, rcMenu, asset):
        # Asset is a PySide6.QtCore.QModelIndex
        # Get the item
        item = asset.data(Qt.UserRole)
        if item is None:
            return
        print("Item: %s" % item)

        # Check if the item is an asset
        if item["type"] != "asset":
            return
        
        # Create an action named "Create USD Asset" and add it to the context menu
        createUsdAssetAction = QAction( "Create USD Asset", origin)
        createUsdAssetAction.triggered.connect(lambda: self.onCreateUsdAsset(item))
        rcMenu.addAction(createUsdAssetAction)

    def onOpenPBAssetTaskContextMenu(self, origin, rcMenu, widget):
        # Asset is a PySide6.QtCore.QModelIndex
        #Check where the cursor is to launch at the right spot
        entity = origin.getCurrentEntity()
        if not entity or entity["type"] not in ["asset"]:
            return
        widgetType = "department" if widget == origin.lw_departments else "task"
        if widgetType != "task":
            return
        
        #Check the department
        deptItem = origin.lw_departments.currentItem()
        if not deptItem:
            return
        department = deptItem.data(Qt.UserRole)

        #Check existing tasks and their names
        existingTasks = self.core.entities.getCategories(entity, step=department)
        existingBaseTasks = [t for t in existingTasks if not any(c.isdigit() for c in t)]
        #CHECK - self.core.popup("Tasks trouvées: %s" % existingBaseTasks)

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
        
    def onCreateUsdAsset(self, item):
       self.core.popup("Create USD for asset: %s" % item["asset"])
        #    create_asset(item["asset"])

    def onCreateVariant(self, origin, entity, department, taskName, existingTasks):
        #self.core.popup("Create variant for task: %s" % taskName)

        #Check existing tasks and determine the right name
        if f"{taskName}_02" not in existingTasks:
            varTaskName = f"{taskName}_02"
        else:
            varTaskName = None
            for i in range(3, 99):
                candidate = f"{taskName}_{i:02d}"
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
        self.core.popup("Variant créée: %s" % varTaskName)
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
        
    def onStateStartup(self, state):
        if state.className == "Export":
            if self.isMaya():

                lo = state.gb_general.layout()
                
                state.w_setting1 = QWidget()
                state.lo_setting1 = QHBoxLayout(state.w_setting1)
                state.lo_setting1.setContentsMargins(9, 0, 9, 0)
                state.l_setting1 = QLabel("Setting 1:")
                state.chb_setting1 = QCheckBox()
                state.lo_setting1.addWidget(state.l_setting1)
                state.lo_setting1.addStretch()
                state.lo_setting1.addWidget(state.chb_setting1)
                lo.addWidget(state.w_setting1)

                state.chb_setting1.toggled.connect(lambda s: state.stateManager.saveStatesToScene())

    def onStateGetSettings(self, state, settings):
        if state.ClassName == "Export":
            if self.isMaya():
                settings["settings"] = state.chb_setting1.isChecked()
            if hasattr(state, "gb_submit"):
                settings["setting2"] = state.cb_setting2.currentText()

    def onStateSettingsLoaded(self, state, settings):

        if state.className == "Export":
            if self.isMaya():
                if "setting1" in settings:
                    state.chb_setting1.setChecked(settings["setting1"])

            if hasattr(state, "gb_submit"):
                if "setting2" in settings:
                    idx = state.cb_setting2.findText(settings["setting2"])
                    if idx != -1:
                        state.cb_setting2.setCurrentIndex(idx)
    
    def preExport(self, **kwargs):
        # this function will be executed before the export started

        if self.isMaya():
            checked = kwargs["state"].chb_setting1.isChecked()
            # do things with this setting in the current scene

        if hasattr(kwargs["state"], "gb_submit"):
            option = kwargs["state"].cb_setting2.currentText()
            # do things with this setting in the current scene

    def postExport(self, **kwargs):
        # this function will be executed after the export completed

        if self.core.appPlugin.pluginName == "Houdini":
            checked = kwargs["state"].chb_setting1.isChecked()
            self.core.popup("Exported with setting1: %s" % (bool(checked)))

    def isMaya(self):

        return self.core.appPlugin.pluginName == "Maya"
    
    def isStandalone(self):

        return self.core.appPlugin.pluginName == "Standalone"

    def isHoudini(self):

        return self.core.appPlugin.pluginName == "Houdni"
