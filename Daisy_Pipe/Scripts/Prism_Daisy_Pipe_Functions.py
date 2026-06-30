# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.


name = "CustomExportSettings"
classname = "CustomExportSettings"

import os

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class Prism_EsmaUSD_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

    def onStateStartup(self, state):

        if state.clqssName == "Export":

            if self.core.appPlugin.pluginName == "Maya":

                lo = state.gb_general_layout()

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

            if hasattr(state, "gb_submit"):

                lo = state.gb_submit.layout()

                # create a widget with a label and a combobox
                state.w_setting2 = QWidget()
                state.lo_setting2 = QHBoxLayout(state.w_setting2)
                state.lo_setting2.setContentsMargins(9, 0, 9, 0)
                state.l_setting2 = QLabel("Setting 2:")
                state.cb_setting2 = QComboBox()
                state.cb_setting2.setMinimumWidth(150)
                state.lo_setting2.addWidget(state.l_setting2)
                state.lo_setting2.addStretch()
                state.lo_setting2.addWidget(state.cb_setting2)
                options = ["setting1", "setting2", "Option3"]
                state.cb_setting2.addItems(options)
                lo.addWidget(state.w_setting2)

                # save the state settings when the current dropdown item gets changed
                state.cb_setting2.currentIndexChanged.connect(lambda s: state.stateManager.saveStatesToScene())

    def onStateGetSettings(self, state, settings):
        # this function collects the currents settings from the GUI widgets in order to save the settings

        if state.className == "Export":
            if self.core.appPlugin.pluginName == "Maya":
                settings["setting1"] = state.chb_setting1.isChecked()

            if hasattr(state, "gb_submit"):
                settings["setting2"] = state.cb_setting2.currentText()

    def onStateSettingsLoaded(self, state, settings):
        # this function loads the state settings from a dict to the GUI widgets

        if state.className == "Export":
            if self.core.appPlugin.pluginName == "Maya":
                if "setting1" in settings:
                    state.chb_setting1.setChecked(settings["setting1"])

            if hasattr(state, "gb_submit"):
                if "setting2" in settings:
                    idx = state.cb_setting2.findText(settings["setting2"])
                    if idx != -1:
                        state.cb_setting2.setCurrentIndex(idx)

    def preExport(self, **kwargs):
        # this function will be executed before the export started

        if self.core.appPlugin.pluginName == "Maya":
            checked = kwargs["state"].chb_setting1.isChecked()
            # do things with this setting in the current scene

        if hasattr(kwargs["state"], "gb_submit"):
            option = kwargs["state"].cb_setting2.currentText()
            # do things with this setting in the current scene

    def postExport(self, **kwargs):
        # this function will be executed after the export completed

        if self.core.appPlugin.pluginName == "Maya":
            checked = kwargs["state"].chb_setting1.isChecked()
            self.core.popup("Exported with setting1: %s" % (bool(checked)))
            
    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True

