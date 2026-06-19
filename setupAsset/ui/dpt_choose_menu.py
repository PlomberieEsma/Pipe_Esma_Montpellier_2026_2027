import importlib
import setupAsset.dcc.launcher as launcher_mod
importlib.reload(launcher_mod)

import sys

from setupAsset.dcc.launcher import get_qt, get_main_window

QtWidgets, QtCore, QtGui = get_qt()


class AssetSetupWindow(QtWidgets.QDialog):

    def __init__(self, parent=get_main_window()):
        super().__init__(parent)

        self.setWindowTitle("Asset Setup")
        self.setMinimumSize(300, 500)

        # on macOS, set the window to be a tool window so it keep on top of the main window
        if sys.platform == "darwin":
            self.setWindowFlags(QtCore.Qt.Tool, True)

        self.button_a = QtWidgets.QPushButton("Button A")
        self.button_b = QtWidgets.QPushButton("Button B")

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(self.button_a)
        main_layout.addWidget(self.button_b)
        main_layout.addStretch()

if __name__ == "__main__":
    win = AssetSetupWindow()
    win.show()
    