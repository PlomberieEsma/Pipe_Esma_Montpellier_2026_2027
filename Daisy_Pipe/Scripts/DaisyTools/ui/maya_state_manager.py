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

from PrismUtils.Decorators import err_catcher

class EsmaUsdExportClass(QWidget):
    className = "EsmaUsdExport"   # nom affiché dans le menu "Add state"
    listType = "Export"           # ou "Import" — la liste dans laquelle il se range

    def setup(self, state, core, stateManager, stateData=None):
        self.core = core
        self.state = state
        self.stateManager = stateManager
        self.canSetVersion = True
        self.nodes = []
        self.setupUi()
        self.connectEvents()
        self.e_departmentLayer.setEnabled(not self.chb_departmentFromScene.isChecked())
        self.initializeContextDefaults()
        self.initializeExistingSelection()

        if stateData is not None:
            self.loadData(stateData)

    @err_catcher(name=__name__)
    def getCurrentContext(self):
        fileName = self.core.getCurrentFileName()
        return self.core.getScenefileData(fileName) or {}

    @err_catcher(name=__name__)
    def getContextFrameRange(self, context, rangeType):
        # mirrors Prism's own default Export state (default_Export.py::getFrameRange),
        # trimmed to the range types this state exposes
        if rangeType == "Single Frame":
            if hasattr(self.core.appPlugin, "getCurrentFrame"):
                frame = int(self.core.appPlugin.getCurrentFrame())
                return frame, frame
            return None, None

        if rangeType in ("Shot", "Shot + 1") and context.get("type") == "shot" and "sequence" in context:
            frange = self.core.entities.getShotRange(context)
            if frange and frange[0] is not None and frange[1] is not None:
                start, end = int(frange[0]), int(frange[1])
                if rangeType == "Shot + 1":
                    start -= 1
                    end += 1
                return start, end

        if hasattr(self.core.appPlugin, "getFrameRange"):
            start, end = self.core.appPlugin.getFrameRange(self)
            if start is not None and end is not None:
                return int(start), int(end)

        return None, None

    @err_catcher(name=__name__)
    def refreshFrameRange(self, rangeType):
        self.updateRangeVisibility(rangeType)
        if rangeType == "Custom":
            return

        context = self.getCurrentContext()
        start, end = self.getContextFrameRange(context, rangeType)
        if start is not None:
            self.sp_rangeStart.setValue(start)
            self.l_rangeStart.setText(str(start))
        if end is not None:
            self.sp_rangeEnd.setValue(end)
            self.l_rangeEnd.setText(str(end))

    @err_catcher(name=__name__)
    def setRangeType(self, rangeType):
        idx = self.cb_rangeType.findText(rangeType)
        if idx != -1:
            self.cb_rangeType.setCurrentIndex(idx)
            self.refreshFrameRange(rangeType)

    @err_catcher(name=__name__)
    def getEntityName(self, context):
        if context.get("type") == "asset":
            return context.get("asset", "")
        if context.get("type") == "shot":
            return f"{context.get('sequence', '')}_{context.get('shot', '')}"
        return ""

    @err_catcher(name=__name__)
    def initializeContextDefaults(self):
        context = self.getCurrentContext()

        department = context.get("department")
        if department:
            self.e_departmentLayer.setText(department)

        entityName = self.getEntityName(context)
        if entityName:
            self.e_parentPrim.setText(entityName)

        if context.get("type") != "shot":
            # "Shot"/"Shot + 1" need a shot's cut range from Prism - not applicable otherwise
            for rangeType in ("Shot + 1", "Shot"):
                idx = self.cb_rangeType.findText(rangeType)
                if idx != -1:
                    self.cb_rangeType.removeItem(idx)

        if context.get("type") == "asset":
            self.setRangeType("Single Frame")
            self.cb_outputType.setCurrentText(".usdc")
        elif context.get("type") == "shot":
            self.setRangeType("Shot")
        else:
            self.setRangeType("Scene")

    @err_catcher(name=__name__)
    def getDefaultPrim(self):
        if self.chb_parentPrim.isChecked() and self.e_parentPrim.text().strip():
            return self.e_parentPrim.text().strip()

        return self.getEntityName(self.getCurrentContext())

    @err_catcher(name=__name__)
    def initializeExistingSelection(self):
        # if this entity already has an export selection set or group in the
        # scene (from a previous export), reflect it in the Maya Objects list
        # instead of leaving it empty
        default_prim = self.getDefaultPrim()
        if not default_prim:
            return

        # pyrefly: ignore [missing-import]
        import maya.cmds as cmds

        geo_set_name = default_prim + "_geo"
        if cmds.objExists(geo_set_name) and cmds.nodeType(geo_set_name) == "objectSet":
            members = cmds.sets(geo_set_name, query=True) or []
            if members:
                self.nodes = members
                self.lw_objects.clear()
                for node in members:
                    self.lw_objects.addItem(node.split("|")[-1])
            return

        group_path = "|" + default_prim
        if cmds.objExists(group_path) and cmds.nodeType(group_path) == "transform":
            self.nodes = [group_path]
            self.lw_objects.clear()
            self.lw_objects.addItem(default_prim)

    @err_catcher(name=__name__)
    def loadData(self, data):
        if "statename" in data:
            self.e_name.setText(data["statename"])
        if "stateenabled" in data and type(data["stateenabled"]) == int:
            self.state.setCheckState(0, Qt.CheckState(data["stateenabled"]))

        self.core.callback("onStateSettingsLoaded", self, data)

    @err_catcher(name=__name__)
    def _makeOverrideRow(self, default_text="", checkbox_label=None):
        # checkbox + line edit, used by every "override" field
        row = QWidget()
        lo_row = QHBoxLayout(row)
        lo_row.setContentsMargins(0, 0, 0, 0)

        chb = QCheckBox(checkbox_label or "")
        e = QLineEdit(default_text)

        lo_row.addWidget(chb)
        lo_row.addWidget(e)

        return row, chb, e

    @err_catcher(name=__name__)
    def setupUi(self):
        self.lo_main = QVBoxLayout(self)

        self.w_name = QWidget()
        self.lo_name = QHBoxLayout(self.w_name)
        self.l_name = QLabel("Name:")
        self.e_name = QLineEdit()
        self.e_name.setText(self.state.text(0))
        self.l_name.setVisible(False)
        self.e_name.setVisible(False)
        self.lo_name.addWidget(self.l_name)
        self.lo_name.addWidget(self.e_name)
        self.lo_main.addWidget(self.w_name)

        # ------------------------------------------------------------ Source
        self.gb_source = QGroupBox("Source")
        self.lo_source = QVBoxLayout(self.gb_source)

        self.w_wholeScene = QWidget()
        self.lo_wholeScene = QHBoxLayout(self.w_wholeScene)
        self.l_wholeScene = QLabel("Export whole Scene:")
        self.chb_wholeScene = QCheckBox()
        self.lo_wholeScene.addWidget(self.l_wholeScene)
        self.lo_wholeScene.addStretch()
        self.lo_wholeScene.addWidget(self.chb_wholeScene)

        self.w_parentPrim = QWidget()
        self.lo_parentPrim = QHBoxLayout(self.w_parentPrim)
        self.l_parentPrim = QLabel("Parent USD Prim:")
        (
            self.row_parentPrim,
            self.chb_parentPrim,
            self.e_parentPrim,
        ) = self._makeOverrideRow()
        self.lo_parentPrim.addWidget(self.l_parentPrim)
        self.lo_parentPrim.addWidget(self.row_parentPrim)

        self.l_objects = QLabel("Maya Objects")
        self.lw_objects = QListWidget()
        self.lw_objects.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lw_objects.setStyleSheet(
            "QListWidget { border: 3px solid rgb(200,0,0); }"
        )
        self.b_addSelected = QPushButton("Add selected")

        self.lo_source.addWidget(self.w_wholeScene)
        self.lo_source.addWidget(self.w_parentPrim)
        self.lo_source.addWidget(self.l_objects)
        self.lo_source.addWidget(self.lw_objects)
        self.lo_source.addWidget(self.b_addSelected)

        # ------------------------------------------------------------ Target
        self.gb_target = QGroupBox("Target")
        self.lo_target = QVBoxLayout(self.gb_target)

        self.w_departmentLayer = QWidget()
        self.lo_departmentLayer = QHBoxLayout(self.w_departmentLayer)
        self.l_departmentLayer = QLabel("Departmentlayer:")
        (
            self.row_departmentLayer,
            self.chb_departmentFromScene,
            self.e_departmentLayer,
        ) = self._makeOverrideRow(
            default_text="not in a departement", checkbox_label="From Scenefile"
        )
        self.chb_departmentFromScene.setChecked(True)
        self.lo_departmentLayer.addWidget(self.l_departmentLayer)
        self.lo_departmentLayer.addWidget(self.row_departmentLayer)

        self.w_master = QWidget()
        self.lo_master = QHBoxLayout(self.w_master)
        self.l_master = QLabel("Update Master Version:")
        self.chb_master = QCheckBox()
        self.chb_master.setChecked(True)
        self.lo_master.addWidget(self.l_master)
        self.lo_master.addStretch()
        self.lo_master.addWidget(self.chb_master)

        self.w_updateThumbnail = QWidget()
        self.lo_updateThumbnail = QHBoxLayout(self.w_updateThumbnail)
        self.l_updateThumbnail = QLabel("Update Thumbnail:")
        self.chb_updateThumbnail = QCheckBox()
        self.chb_updateThumbnail.setChecked(True)
        self.lo_updateThumbnail.addWidget(self.l_updateThumbnail)
        self.lo_updateThumbnail.addStretch()
        self.lo_updateThumbnail.addWidget(self.chb_updateThumbnail)

        self.w_outputType = QWidget()
        self.lo_outputType = QHBoxLayout(self.w_outputType)
        self.l_outputType = QLabel("Outputtype:")
        self.cb_outputType = QComboBox()
        self.cb_outputType.addItems([".usda", ".usdc", ".usdz"])
        self.cb_outputType.setCurrentText(".usdc")
        self.lo_outputType.addWidget(self.l_outputType)
        self.lo_outputType.addStretch()
        self.lo_outputType.addWidget(self.cb_outputType)

        self.lo_target.addWidget(self.w_departmentLayer)
        self.lo_target.addWidget(self.w_master)
        self.lo_target.addWidget(self.w_updateThumbnail)
        self.lo_target.addWidget(self.w_outputType)

        # ----------------------------------------------------------- Settings
        self.gb_settings = QGroupBox("Settings")
        self.lo_settings = QVBoxLayout(self.gb_settings)

        self.w_rangeType = QWidget()
        self.lo_rangeType = QHBoxLayout(self.w_rangeType)
        self.l_rangeTypeLbl = QLabel("Framerange:")
        self.cb_rangeType = QComboBox()
        self.cb_rangeType.addItems(
            ["Scene", "Shot", "Shot + 1", "Single Frame", "Custom"]
        )
        self.lo_rangeType.addWidget(self.l_rangeTypeLbl)
        self.lo_rangeType.addStretch()
        self.lo_rangeType.addWidget(self.cb_rangeType)

        self.w_rangeStart = QWidget()
        self.lo_rangeStart = QHBoxLayout(self.w_rangeStart)
        self.l_startLbl = QLabel("Start:")
        self.l_rangeStart = QLabel("1")
        self.sp_rangeStart = QSpinBox()
        self.sp_rangeStart.setRange(-9999, 9999)
        self.sp_rangeStart.setValue(1)
        self.lo_rangeStart.addWidget(self.l_startLbl)
        self.lo_rangeStart.addStretch()
        self.lo_rangeStart.addWidget(self.l_rangeStart)
        self.lo_rangeStart.addWidget(self.sp_rangeStart)

        self.w_rangeEnd = QWidget()
        self.lo_rangeEnd = QHBoxLayout(self.w_rangeEnd)
        self.l_endLbl = QLabel("End:")
        self.l_rangeEnd = QLabel("120")
        self.sp_rangeEnd = QSpinBox()
        self.sp_rangeEnd.setRange(-9999, 9999)
        self.sp_rangeEnd.setValue(120)
        self.lo_rangeEnd.addWidget(self.l_endLbl)
        self.lo_rangeEnd.addStretch()
        self.lo_rangeEnd.addWidget(self.l_rangeEnd)
        self.lo_rangeEnd.addWidget(self.sp_rangeEnd)

        self.w_animationType = QWidget()
        self.lo_animationType = QHBoxLayout(self.w_animationType)
        self.l_animationType = QLabel("Animation Type:")
        self.cb_animationType = QComboBox()
        self.cb_animationType.addItems(["Time Samples", "File per Frame"])
        self.lo_animationType.addWidget(self.l_animationType)
        self.lo_animationType.addStretch()
        self.lo_animationType.addWidget(self.cb_animationType)

        self.w_exportUVs = QWidget()
        self.lo_exportUVs = QHBoxLayout(self.w_exportUVs)
        self.l_exportUVs = QLabel("Export UVs:")
        self.chb_exportUVs = QCheckBox()
        self.chb_exportUVs.setChecked(True)
        self.lo_exportUVs.addWidget(self.l_exportUVs)
        self.lo_exportUVs.addStretch()
        self.lo_exportUVs.addWidget(self.chb_exportUVs)

        self.w_subdivision = QWidget()
        self.lo_subdivision = QHBoxLayout(self.w_subdivision)
        self.l_subdivision = QLabel("Subdivision Method:")
        self.cb_subdivision = QComboBox()
        self.cb_subdivision.addItems(["Catmull-Clark", "Bilinear", "Loop", "None"])
        self.lo_subdivision.addWidget(self.l_subdivision)
        self.lo_subdivision.addStretch()
        self.lo_subdivision.addWidget(self.cb_subdivision)

        self.lo_settings.addWidget(self.w_rangeType)
        self.lo_settings.addWidget(self.w_rangeStart)
        self.lo_settings.addWidget(self.w_rangeEnd)
        self.lo_settings.addWidget(self.w_animationType)
        self.lo_settings.addWidget(self.w_exportUVs)
        self.lo_settings.addWidget(self.w_subdivision)

        self.lo_main.addWidget(self.gb_source)
        self.lo_main.addWidget(self.gb_target)
        self.lo_main.addWidget(self.gb_settings)

        self.updateRangeVisibility(self.cb_rangeType.currentText())

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.e_name.textChanged.connect(self.nameChanged)
        self.e_name.editingFinished.connect(self.stateManager.saveStatesToScene)

        self.chb_wholeScene.toggled.connect(self.wholeSceneToggled)
        self.chb_parentPrim.toggled.connect(self.e_parentPrim.setEnabled)
        self.chb_departmentFromScene.toggled.connect(
            lambda checked: self.e_departmentLayer.setEnabled(not checked)
        )
        self.cb_rangeType.currentTextChanged.connect(self.refreshFrameRange)
        self.b_addSelected.clicked.connect(self.addSelected)

    @err_catcher(name=__name__)
    def wholeSceneToggled(self, checked):
        self.lw_objects.setEnabled(not checked)
        self.b_addSelected.setEnabled(not checked)

    @err_catcher(name=__name__)
    def updateRangeVisibility(self, rangeType):
        isCustom = rangeType == "Custom"
        self.l_rangeStart.setVisible(not isCustom)
        self.l_rangeEnd.setVisible(not isCustom)
        self.sp_rangeStart.setVisible(isCustom)
        self.sp_rangeEnd.setVisible(isCustom)

    @err_catcher(name=__name__)
    def addSelected(self):
        # pyrefly: ignore [missing-import]
        import maya.cmds as cmds

        selection = cmds.ls(selection=True, long=True)
        if not selection:
            self.core.popup("Nothing selected in the scene.", title="EsmaUsdExport", severity="warning")
            return

        self.nodes = selection
        self.lw_objects.clear()
        for node in selection:
            self.lw_objects.addItem(node.split("|")[-1])

    @err_catcher(name=__name__)
    def nameChanged(self, text):
        self.state.setText(0, text)

    @err_catcher(name=__name__)
    def updateUi(self):
        return True

    @err_catcher(name=__name__)
    def getExportParams(self):
        # plain dict, no Qt objects - this is what exportUSD.export_usd() consumes
        return {
            "department": self.e_departmentLayer.text().strip(),
            "whole_scene": self.chb_wholeScene.isChecked(),
            "nodes": list(self.nodes),
            "default_prim_override": (
                self.e_parentPrim.text().strip()
                if self.chb_parentPrim.isChecked() and self.e_parentPrim.text().strip()
                else None
            ),
            "extension": self.cb_outputType.currentText(),
            "update_master": self.chb_master.isChecked(),
            "update_thumbnail": self.chb_updateThumbnail.isChecked(),
            "export_uvs": self.chb_exportUVs.isChecked(),
            "subdivision_method": self.cb_subdivision.currentText(),
            "animation_type": self.cb_animationType.currentText(),
            "start_frame": self.sp_rangeStart.value(),
            "end_frame": self.sp_rangeEnd.value(),
        }

    @err_catcher(name=__name__)
    def preExecuteState(self):
        warnings = []
        if not self.chb_wholeScene.isChecked() and not self.nodes:
            warnings.append(["No objects in the Maya Objects list.", "", 3])
        return [self.state.text(0), warnings]

    @err_catcher(name=__name__)
    def executeState(self, parent, useVersion="next"):
        from DaisyTools.saveas.exportUSD import export_usd

        if not self.chb_wholeScene.isChecked() and not self.nodes:
            return [
                self.state.text(0)
                + ": error - No objects in the Maya Objects list. Add objects or check 'Export whole Scene'."
            ]

        try:
            outputPath = export_usd(self.getExportParams())
        except Exception as e:
            return [self.state.text(0) + " - error - %s" % e]

        if not outputPath:
            return [self.state.text(0) + " - error"]

        result = self.core.popupQuestion(
            "USD export: %s" % outputPath,
            title="EsmaUsdExport",
            buttons=["Open in Explorer", "Ok"],
            default="Ok",
        )
        if result == "Open in Explorer":
            self.core.openFolder(outputPath)

        return [self.state.text(0) + " - success"]

    @err_catcher(name=__name__)
    def getStateProps(self):
        stateProps = {}
        stateProps.update(
            {
                "statename": self.e_name.text(),
                "stateenabled": self.core.getCheckStateValue(self.state.checkState(0)),
            }
        )
        return stateProps
