# PrismInit.py
#
# Ce fichier est copie par Prism_SubstancePainter_Integration.addIntegration()
# dans : %USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins
#
# Substance Painter le charge automatiquement au demarrage (menu Python),
# ou manuellement via Python > PrismInit dans le menu de SP.

import os
import sys
import logging
logger = logging.getLogger(__name__)

from PySide6 import QtGui
import substance_painter.ui as sp_ui
import substance_painter.event as sp_event
import substance_painter.project as sp_project

pcore = None
prism_menu = None

# ---------------------------------------------------------------------- #
# 1. Rendre PrismCore importable
# ---------------------------------------------------------------------- #
# Le chemin racine de Prism (Scripts/) doit etre injecte dans sys.path.
# Idealement ce chemin n'est PAS hardcode ici, mais lu depuis une variable
# d'environnement definie a l'installation (PRISM_ROOT), pour rester
# valide meme si Prism est deplace/reinstalle ailleurs.

prismRoot = os.environ.get("PRISM_ROOT", r"C:/Program Files/Prism2")
ICON_PATH = os.path.join(prismRoot, "Plugins", "Apps", "SubstancePainter", "Resources", "daisy_logo.png")

# ---------------------------------------------------------------------- #
# 3. Enregistrer le menu Prism dans l'UI de Substance Painter
# ---------------------------------------------------------------------- #


def open_project_browser():
    if pcore is not None:
        pcore.projectBrowser()

def save_version():
    if pcore is not None:
        pcore.saveScene()

def save_comment():
    if pcore is not None and pcore.appPlugin is not None:
        pcore.appPlugin.SaveComment()

def import_geometry():
    if pcore is not None and pcore.appPlugin is not None:
        pcore.appPlugin.ImportGeometry()

def export_textures():
    if pcore is not None and pcore.appPlugin is not None:
        pcore.appPlugin.ExportTextures()

def start_plugin():
    global pcore, prism_menu

    if pcore is not None:
        # deja demarre, evite une double initialisation
        return

    scriptDir = os.path.join(prismRoot, "Scripts")
    if scriptDir not in sys.path:
        sys.path.append(scriptDir)

    try:
        import PrismCore
    except Exception as e:
        logger.warning("Impossible d'importer PrismCore: %s" % e)
        raise

    pcore = PrismCore.PrismCore(app="SubstancePainter")

    main_window = sp_ui.get_main_window()
    menu_bar = main_window.menuBar()

    prism_menu = menu_bar.addMenu("Prism")

    if os.path.isfile(ICON_PATH):
        prism_menu.setIcon(QtGui.QIcon(ICON_PATH))

    save_version_action = QtGui.QAction("Save Version", main_window)
    save_version_action.triggered.connect(save_version)
    prism_menu.addAction(save_version_action)

    save_comment_action = QtGui.QAction("Save Comment", main_window)
    save_comment_action.triggered.connect(save_comment)
    prism_menu.addAction(save_comment_action)

    project_browser_action = QtGui.QAction("Project Browser", main_window)
    project_browser_action.triggered.connect(open_project_browser)
    prism_menu.addAction(project_browser_action)

    import_geometry_action = QtGui.QAction("Import Geometry", main_window)
    import_geometry_action.triggered.connect(import_geometry)
    prism_menu.addAction(import_geometry_action)

    export_textures_action = QtGui.QAction("Export Textures", main_window)
    export_textures_action.triggered.connect(export_textures)
    prism_menu.addAction(export_textures_action)



def close_plugin():
    global prism_menu
    if prism_menu is not None:
        main_window = sp_ui.get_main_window()
        main_window.menuBar().removeAction(prism_menu.menuAction())
        prism_menu = None
