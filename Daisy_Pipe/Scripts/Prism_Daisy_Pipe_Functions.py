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

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from functools import partial
import os

from DaisyTools.core.command_launcher import Command_launcher

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class SelectedAssetsList(QTreeWidget):

    #-----------------------------------------------------------------------------------#
    # Class used in the Asset Browser to handle the asset movement between lists        #
    # Actions to Drag and Drop the Asset from the origin list to the selected list      #
    # Action to Delete the Asset from the selected list                                 #
    #-----------------------------------------------------------------------------------#

    
    def __init__(self, parentDlg):
        super(SelectedAssetsList, self).__init__()
        self.parentDlg = parentDlg
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        try:
            self.parentDlg.onAssetsDropped()
        except Exception as e:
            self.parentDlg.core.popup("Erreur drop: %s" % e)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.parentDlg.onRemoveSelectedAssets(self.selectedItems())
        else:
            super(SelectedAssetsList, self).keyPressEvent(event)

class Prism_Daisy_Pipe_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.core.registerCallback("onProjectBrowserStartup", self.onProjectBrowserStartup, plugin=self)
        self.core.registerCallback("openPBAssetContextMenu", self.onOpenPBAssetContextMenu, plugin=self)
        self.core.registerCallback("openPBAssetTaskContextMenu", self.onOpenPBAssetTaskContextMenu, plugin=self)
        self.Command_launcher = Command_launcher(core, plugin)

    # TOP GENERAL Menu
    def onProjectBrowserStartup(self, origin):
        
        #-----------------------------------------------------------------------------------#
        # Create a general menu 'DaisyMenu'                                                 #
        # Create an option 'Asset Browser'                                                  #
        # Launch the opening of the Asset Browser when 'Asset BRowser' is triggered         #
        #-----------------------------------------------------------------------------------#

        origin.daisyMenu = QMenu("DaisyMenu")
        origin.daisyMenu.addAction("Asset Browser", partial(self.onAssetBrowserTriggered, origin))
        origin.menubar.addMenu(origin.daisyMenu)

    def onAssetBrowserTriggered(self, origin, checked=False):
        
        #-----------------------------------------------------------------------------------#
        # Window Asset Browser to select assets to load into a scene during layout          #
        #-----------------------------------------------------------------------------------#

        try:
            allAssetPaths = self.core.entities.getAssetPaths()
            self.assetRoot = os.path.commonpath(allAssetPaths) if allAssetPaths else ""
            
            self.assetBrowserDlg = QDialog(origin)
            self.core.parentWindow(self.assetBrowserDlg, parent=origin)
            self.assetBrowserDlg.setWindowTitle("Asset Browser")
            self.assetBrowserDlg.resize(700, 600)

            mainLayout = QVBoxLayout(self.assetBrowserDlg)
            columnsLayout = QHBoxLayout()
            mainLayout.addLayout(columnsLayout)

            # LEFT COLUMN : Prism Asset List
            import EntityWidget
            self.w_entities = EntityWidget.EntityWidget(core=self.core, refresh=True)
            # Keep only necessary and hide shots
            self.w_entities.tb_entities.setVisible(False)
            self.w_entities.getPage("Assets").tw_tree.setDragEnabled(True)
            self.selectedAssetsData = {}  # clé = asset_path (unique), valeur = entity dict
            columnsLayout.addWidget(self.w_entities)

            # RIGHT COLUMN : Selected Assets
            self.gb_selectedAssets = QGroupBox("Selected Assets")
            lo_selectedAssets = QVBoxLayout()
            self.gb_selectedAssets.setLayout(lo_selectedAssets)
            self.lw_selectedAssets = SelectedAssetsList(self)
            lo_selectedAssets.addWidget(self.lw_selectedAssets)
            columnsLayout.addWidget(self.gb_selectedAssets)

            # BOTTOM : Validate Button
            self.btn_validate = QPushButton("Validate")
            self.btn_validate.clicked.connect(self.onValidateAssetsBrowser)
            mainLayout.addWidget(self.btn_validate)

            self.assetBrowserDlg.show()
        except Exception as e:
            self.core.popup("Erreur AssetBrowser: %s" % e)

    def onAssetsDropped(self):
        
        #-----------------------------------------------------------------------------------#
        # Add asset to the 'Selected Assets' list then refresh list                         #
        #-----------------------------------------------------------------------------------#

        entities = self.w_entities.getCurrentData(returnOne=False)
        entities = [e for e in entities if e["type"] == "asset"]

        for entity in entities:
            key = entity.get("asset_path")
            if key and key not in self.selectedAssetsData:
                self.selectedAssetsData[key] = entity

        self.refreshSelectedAssetsList()

    def refreshSelectedAssetsList(self):
         
        #-----------------------------------------------------------------------------------#
        # Refresh the 'Selected Assets' list                                                #
        #-----------------------------------------------------------------------------------#

        self.lw_selectedAssets.clear()
        self.lw_selectedAssets.setIconSize(QSize(50, 50))

        assets = list(self.selectedAssetsData.values())
        if not assets:
            return

        nodes = {}
        for entity in assets:
            relPath = entity.get("asset_path", "")
            parts = relPath.replace("\\", "/").split("/")

            parent = self.lw_selectedAssets
            currentPath = ""
            for i, part in enumerate(parts):
                currentPath = os.path.join(currentPath, part)
                if currentPath not in nodes:
                    if parent is self.lw_selectedAssets:
                        node = QTreeWidgetItem(self.lw_selectedAssets, [part])
                    else:
                        node = QTreeWidgetItem(parent, [part])
                    nodes[currentPath] = node
                else:
                    node = nodes[currentPath]

                if i == len(parts) - 1:
                    node.setData(0, Qt.UserRole, entity)
                    pm = self.core.entities.getEntityPreview(entity)
                    if not pm:
                        pm = self.core.media.emptyPrvPixmap
                    node.setIcon(0, QIcon(pm))

                parent = node

        self.lw_selectedAssets.expandAll()

    def onRemoveSelectedAssets(self, items):
         
        #-----------------------------------------------------------------------------------#
        # Delete asset to the 'Selected Assets' list then refresh list                      #
        #-----------------------------------------------------------------------------------#

        for item in items:
            entity = item.data(0, Qt.UserRole)
            if not entity:
                continue  # c'est un dossier, pas un asset - on ignore
            key = entity.get("asset_path")
            if key in self.selectedAssetsData:
                del self.selectedAssetsData[key]
        self.refreshSelectedAssetsList()

    def onValidateAssetsBrowser(self):
         
        #-----------------------------------------------------------------------------------------#
        # Output the list of selected asset in the Asset Browser with their path as a dictionary  #
        #-----------------------------------------------------------------------------------------#

        output = {}
        for entity in self.selectedAssetsData.values():
            name = entity.get("asset", "")
            path = entity.get("paths", "")
            output[name] = path
        return output














    ##############################################################################################################
    ###########################     ASSET Contextual Menu - Create USD      ######################################
    ##############################################################################################################
    def onOpenPBAssetContextMenu(self, origin, rcMenu, asset):
        
        #-----------------------------------------------------------------------------------#
        # Add an option "CreateUSD Asset" to the context menu for assets                    #
        # When clicked, launch the function onCreateUsdAsset with the asset as argument     #
        #-----------------------------------------------------------------------------------#
        
        # Asset is a PySide6.QtCore.QModelIndex
        # Get the item
        item = asset.data(Qt.UserRole)
        if item is None:
            return
        self.core.popup("Item: %s" % item)

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
    def onOpenPBAssetTaskContextMenu(self, origin, rcMenu, widget):
        
        #-----------------------------------------------------------------------------------#
        # Create a submenu "Add Variants" to the context menu for assets' task              #
        # Add as options every current existing task                                        #
        # When clicked, launch the function onCreateVariant with the task as argument       #
        #-----------------------------------------------------------------------------------#
        
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
        
    def onCreateVariant(self, origin, entity, department, taskName, existingTasks):
        
        #-----------------------------------------------------------------------------------#
        # Get the chosen task from the Create Variant option                                #
        # Create the task with the same name and variant increment                          #
        #-----------------------------------------------------------------------------------#
        
        #Check existing tasks and determine the right name
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

