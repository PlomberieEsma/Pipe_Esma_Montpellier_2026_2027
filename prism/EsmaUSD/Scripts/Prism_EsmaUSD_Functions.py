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


from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_EsmaUSD_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.core.registerCallback("onProjectBrowserStartup", self.onProjectBrowserStartup, plugin=self)

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True

    @err_catcher(name=__name__)
    def onProjectBrowserStartup(self, origin):
        # Find the index of the "Products" tab to insert "Test" before it
        tbw = origin.tbw_project
        products_index = -1
        for i in range(tbw.count()):
            if tbw.tabText(i).lower() == "products":
                products_index = i
                break

        # Create the Test tab widget
        w_test = QWidget()
        layout = QVBoxLayout(w_test)
        label = QLabel("Test Menu - EsmaUSD Plugin")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Insert the tab before "Products" (or at the end if not found)
        insert_index = products_index if products_index >= 0 else tbw.count()
        tbw.insertTab(insert_index, w_test, "Test")
