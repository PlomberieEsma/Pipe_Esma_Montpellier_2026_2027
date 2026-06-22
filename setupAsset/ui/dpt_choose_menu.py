import importlib
import setupAsset.dcc.launcher as launcher_mod
importlib.reload(launcher_mod)

import sys

from setupAsset.dcc.launcher import get_qt, get_main_window

QtWidgets, QtCore, QtGui = get_qt()

class AssetSetupWindow(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(AssetSetupWindow, self).__init__(parent)

        self.setWindowTitle("Open/Import/Reference")
        self.setMinimumSize(400, 100)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.filepath_le = QtWidgets.QLineEdit()
        self.browse_btn = QtWidgets.QPushButton()
        self.browse_btn.setIcon(QtGui.QIcon(":/fileOpen.png"))
        
        self.open_rb = QtWidgets.QRadioButton("Open")
        self.open_rb.setChecked(True)
        
        self.import_rb = QtWidgets.QRadioButton("Import")
        self.reference_rb = QtWidgets.QRadioButton("Reference")
        
        self.force_cb = QtWidgets.QCheckBox("Force")
        
        self.aplly_btn = QtWidgets.QPushButton("Apply")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.browse_btn)
        
        radio_btn_layout = QtWidgets.QHBoxLayout()
        radio_btn_layout.addWidget(self.open_rb)
        radio_btn_layout.addWidget(self.import_rb)
        radio_btn_layout.addWidget(self.reference_rb)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("File Path:", file_path_layout)
        form_layout.addRow("", radio_btn_layout)
        form_layout.addRow("", self.force_cb)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.aplly_btn)
        btn_layout.addWidget(self.close_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        pass

if __name__ == "__main__":
    
    try:
        open_import_dialog.close() # type: ignore
        open_import_dialog.deleteLater() # type: ignore
    except:
        pass

    open_import_dialog = AssetSetupWindow()
    open_import_dialog.show()
    