# initializer and core of Pyful
#
# Copyright (C) 2010-2011 anmitsu <anmitsu.s@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""pyful - Python file management utility.

This application is CUI filer of the keyboard operation for Linux.
"""

__version__ = "0.2.2"

__all__ = ["cmdline", "command", "filectrl", "filer", "help", "look", "menu",
           "message", "mode", "process", "ui", "util", "completion", "widget"]

import os
import shutil

from pyful import ui

class Pyful(object):
    """PYthon File management UtiLity"""

    environs = {
        "EDITOR": "vim",
        "PAGER": "less",
        "RCFILE": os.path.join(os.getenv("HOME"), ".pyful", "rc.py"),
        "SCRIPT": "",
        }
    initfuncs = []
    exitfuncs = []

    @classmethod
    def atinit(cls, func):
        cls.initfuncs.append(func)
        return func

    @classmethod
    def atexit(cls, func):
        cls.exitfuncs.append(func)
        return func

    def __init__(self, binpath):
        self.environs["SCRIPT"] = binpath
        ui.start_widget()

    def init_function(self):
        for func in self.initfuncs: func()

    def exit_function(self):
        for func in self.exitfuncs: func()

    def loadrcfile(self, path=None):
        if path is None:
            libpath = os.path.dirname(os.path.abspath(__file__))
            defpath = os.path.join(libpath, "rc.py")
            path = os.path.expanduser(self.environs["RCFILE"])
            if not os.path.exists(path):
                path = defpath
        try:
            with open(path, "r") as rc:
                exec(rc.read(), locals())
            self.environs["RCFILE"] = path
        except Exception as e:
            with open(defpath, "r") as rc:
                exec(rc.read(), locals())
            self.environs["RCFILE"] = defpath
            return e

    def savercfile(self):
        confdir = os.path.join(os.getenv("HOME"), ".pyful")
        if not os.path.exists(confdir):
            os.makedirs(confdir, 0o700)
        rcfile = os.path.join(confdir, "rc.py")
        if not os.path.exists(rcfile):
            libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            default = os.path.join(libdir, "rc.py")
            shutil.copy(default, rcfile)

    def main_loop(self):
        viewer = ui.Viewer()
        controller = ui.Controller()
        while True:
            viewer.view_and_update()
            controller.control()
