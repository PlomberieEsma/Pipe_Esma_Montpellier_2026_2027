import os

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
        self.setupUi()
        self.connectEvents()

        if stateData is not None:
            self.loadData(stateData)

    @err_catcher(name=__name__)
    def loadData(self, data):
        if "statename" in data:
            self.e_name.setText(data["statename"])
        if "stateenabled" in data and self.listType == "Export":
            self.state.setCheckState(
                0,
                eval(
                    data["stateenabled"]
                    .replace("PySide.QtCore.", "")
                    .replace("PySide2.QtCore.", "")
                ),
            )

        self.core.callback("onStateSettingsLoaded", self, data)

    @err_catcher(name=__name__)
    def _makeOverrideRow(self, default_text="", checkbox_label=None):
        # checkbox + line edit + dropdown tool button, used by every
        # "override" field in the Source/Target/Settings groups
        row = QWidget()
        lo_row = QHBoxLayout(row)
        lo_row.setContentsMargins(0, 0, 0, 0)

        chb = QCheckBox(checkbox_label or "")
        e = QLineEdit(default_text)
        b = QToolButton()
        b.setText(u"▼")
        b.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(b)
        placeholder = menu.addAction("No presets yet")
        placeholder.setEnabled(False)
        b.setMenu(menu)

        lo_row.addWidget(chb)
        lo_row.addWidget(e)
        lo_row.addWidget(b)

        return row, chb, e, b

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

        self.w_exportType = QWidget()
        self.lo_exportType = QHBoxLayout(self.w_exportType)
        self.l_exportType = QLabel("Export Type:")
        self.cb_exportType = QComboBox()
        self.cb_exportType.addItems(["Scene Objects", "USD Layer"])
        self.lo_exportType.addWidget(self.l_exportType)
        self.lo_exportType.addStretch()
        self.lo_exportType.addWidget(self.cb_exportType)

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
            self.b_parentPrim,
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

        self.lo_source.addWidget(self.w_exportType)
        self.lo_source.addWidget(self.w_wholeScene)
        self.lo_source.addWidget(self.w_parentPrim)
        self.lo_source.addWidget(self.l_objects)
        self.lo_source.addWidget(self.lw_objects)
        self.lo_source.addWidget(self.b_addSelected)

        # ------------------------------------------------------------ Target
        self.gb_target = QGroupBox("Target")
        self.lo_target = QVBoxLayout(self.gb_target)

        self.w_entity = QWidget()
        self.lo_entity = QHBoxLayout(self.w_entity)
        self.l_entity = QLabel("Entity:")
        self.cb_entity = QComboBox()
        self.cb_entity.addItems(["From Scenefile", "Custom"])
        self.lo_entity.addWidget(self.l_entity)
        self.lo_entity.addStretch()
        self.lo_entity.addWidget(self.cb_entity)

        self.w_saveAs = QWidget()
        self.lo_saveAs = QHBoxLayout(self.w_saveAs)
        self.l_saveAs = QLabel("Save As:")
        self.cb_saveAs = QComboBox()
        self.cb_saveAs.addItems(["Full USD Container", "Layer", "Custom"])
        self.lo_saveAs.addWidget(self.l_saveAs)
        self.lo_saveAs.addStretch()
        self.lo_saveAs.addWidget(self.cb_saveAs)

        self.l_layer = QLabel("Layer")

        self.w_departmentLayer = QWidget()
        self.lo_departmentLayer = QHBoxLayout(self.w_departmentLayer)
        self.lo_departmentLayer.setContentsMargins(20, 0, 0, 0)
        self.l_departmentLayer = QLabel("Departmentlayer:")
        (
            self.row_departmentLayer,
            self.chb_departmentFromScene,
            self.e_departmentLayer,
            self.b_departmentLayer,
        ) = self._makeOverrideRow(
            default_text="09_compositing", checkbox_label="From Scenefile"
        )
        self.chb_departmentFromScene.setChecked(True)
        self.lo_departmentLayer.addWidget(self.l_departmentLayer)
        self.lo_departmentLayer.addWidget(self.row_departmentLayer)

        self.w_sublayer = QWidget()
        self.lo_sublayer = QHBoxLayout(self.w_sublayer)
        self.lo_sublayer.setContentsMargins(20, 0, 0, 0)
        self.l_sublayer = QLabel("Sublayer:")
        (
            self.row_sublayer,
            self.chb_sublayerOverride,
            self.e_sublayer,
            self.b_sublayer,
        ) = self._makeOverrideRow(default_text="main")
        self.lo_sublayer.addWidget(self.l_sublayer)
        self.lo_sublayer.addWidget(self.row_sublayer)

        self.w_master = QWidget()
        self.lo_master = QHBoxLayout(self.w_master)
        self.l_master = QLabel("Update Master Version:")
        self.chb_master = QCheckBox()
        self.chb_master.setChecked(True)
        self.lo_master.addWidget(self.l_master)
        self.lo_master.addStretch()
        self.lo_master.addWidget(self.chb_master)

        self.w_outputType = QWidget()
        self.lo_outputType = QHBoxLayout(self.w_outputType)
        self.l_outputType = QLabel("Outputtype:")
        self.cb_outputType = QComboBox()
        self.cb_outputType.addItems([".usda", ".usdc", ".usdz"])
        self.cb_outputType.setCurrentText(".usdc")
        self.lo_outputType.addWidget(self.l_outputType)
        self.lo_outputType.addStretch()
        self.lo_outputType.addWidget(self.cb_outputType)

        self.lo_target.addWidget(self.w_entity)
        self.lo_target.addWidget(self.w_saveAs)
        self.lo_target.addWidget(self.l_layer)
        self.lo_target.addWidget(self.w_departmentLayer)
        self.lo_target.addWidget(self.w_sublayer)
        self.lo_target.addWidget(self.w_master)
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

        self.w_mergePrevious = QWidget()
        self.lo_mergePrevious = QHBoxLayout(self.w_mergePrevious)
        self.l_mergePrevious = QLabel("Merge with previous version:")
        (
            self.row_mergePrevious,
            self.chb_mergePrevious,
            self.e_mergePrevious,
            self.b_mergePrevious,
        ) = self._makeOverrideRow(default_text="latest")
        self.lo_mergePrevious.addWidget(self.l_mergePrevious)
        self.lo_mergePrevious.addWidget(self.row_mergePrevious)

        self.b_showPreviousContent = QPushButton("Show Previous Version Content")
        self.b_additionalSettings = QPushButton("Additional Settings...")

        self.lo_settings.addWidget(self.w_rangeType)
        self.lo_settings.addWidget(self.w_rangeStart)
        self.lo_settings.addWidget(self.w_rangeEnd)
        self.lo_settings.addWidget(self.w_animationType)
        self.lo_settings.addWidget(self.w_exportUVs)
        self.lo_settings.addWidget(self.w_subdivision)
        self.lo_settings.addWidget(self.w_mergePrevious)
        self.lo_settings.addWidget(self.b_showPreviousContent)
        self.lo_settings.addWidget(self.b_additionalSettings)

        # ------------------------------------------------------ Previous export
        self.gb_previousExport = QGroupBox("Previous export")
        self.lo_previousExport = QVBoxLayout(self.gb_previousExport)
        self.cb_previousExport = QComboBox()
        self.cb_previousExport.addItems(["None"])
        self.lo_previousExport.addWidget(self.cb_previousExport)

        self.lo_main.addWidget(self.gb_source)
        self.lo_main.addWidget(self.gb_target)
        self.lo_main.addWidget(self.gb_settings)
        self.lo_main.addWidget(self.gb_previousExport)

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
        self.chb_sublayerOverride.toggled.connect(self.e_sublayer.setEnabled)
        self.chb_mergePrevious.toggled.connect(self.e_mergePrevious.setEnabled)
        self.cb_rangeType.currentTextChanged.connect(self.updateRangeVisibility)
        self.b_addSelected.clicked.connect(self.addSelected)
        self.b_showPreviousContent.clicked.connect(self.showPreviousVersionContent)
        self.b_additionalSettings.clicked.connect(self.showAdditionalSettings)

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
        self.core.popup("Not implemented yet.", title="EsmaUsdExport", severity="info")

    @err_catcher(name=__name__)
    def showPreviousVersionContent(self):
        self.core.popup("Not implemented yet.", title="EsmaUsdExport", severity="info")

    @err_catcher(name=__name__)
    def showAdditionalSettings(self):
        self.core.popup("Not implemented yet.", title="EsmaUsdExport", severity="info")

    @err_catcher(name=__name__)
    def nameChanged(self, text):
        self.state.setText(0, text)

    @err_catcher(name=__name__)
    def updateUi(self):
        return True

    @err_catcher(name=__name__)
    def preExecuteState(self):
        warnings = []
        return [self.state.text(0), warnings]

    @err_catcher(name=__name__)
    def executeState(self, parent, useVersion="next"):
        fileName = self.core.getCurrentFileName()
        context = self.core.getScenefileData(fileName)
        outputPath = self.core.products.generateProductPath(
            entity=context,
            task="myProduct",
            extension=self.cb_outputType.currentText(),
        )

        if not os.path.exists(os.path.dirname(outputPath)):
            os.makedirs(os.path.dirname(outputPath))

        with open(outputPath, "w") as f:
            f.write("custom export")

        self.core.popup("Custom export to: %s" % outputPath, severity="info")
        result = {"result": "success"}
        if result["result"] == "success":
            return [self.state.text(0) + " - success"]
        else:
            return [
                self.state.text(0)
                + " - error - %s" % result["error"]
            ]

    @err_catcher(name=__name__)
    def getStateProps(self):
        stateProps = {}
        stateProps.update(
            {
                "statename": self.e_name.text(),
                "stateenabled": str(self.state.checkState(0)),
            }
        )
        return stateProps
