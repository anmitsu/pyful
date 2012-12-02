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

__author__ = "anmitsu <anmitsu.s@gmail.com>"
__version__ = "0.2.2"

__all__ = ["cmdline", "command", "filectrl", "filer", "help", "look", "menu",
           "message", "mode", "process", "util", "completion", "widget"]

import os
import sys

from pyful import look
from pyful import util
from pyful import widget

class Widgets(object):
    @property
    def filer(self):
        return widget.get("Filer")

    @property
    def cmdline(self):
        return widget.get("Cmdline")

    @property
    def menu(self):
        return widget.get("Menu")

    @property
    def message(self):
        return widget.get("Message")

    @property
    def help(self):
        return widget.get("Help")

    @property
    def action(self):
        return widget.get("ActionBox")

widgets = Widgets()

class Pyful(object):
    """PYthon File management UtiLity"""

    environs = {
        "EDITOR": "vim",
        "PAGER": "less",
        "RCFILE": os.path.join(os.getenv("HOME"), ".pyful", "rc.py"),
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

    def __init__(self):
        import pyful.cmdline
        import pyful.filer
        import pyful.message
        import pyful.menu
        import pyful.help
        pyful.cmdline.Cmdline()
        pyful.filer.Filer()
        pyful.message.Message()
        pyful.menu.Menu()
        pyful.help.Help()

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
            util.loadfile(path)
            self.environs["RCFILE"] = path
        except Exception as e:
            util.loadfile(defpath)
            self.environs["RCFILE"] = defpath
            return e

    def draw(self):
        widgets.filer.draw()
        if widgets.menu.active:
            widgets.menu.draw()
        if widgets.help.active:
            widgets.help.draw()
        elif widgets.cmdline.active:
            widgets.cmdline.draw()
        elif widgets.message.active and not widgets.filer.finder.active:
            widgets.message.draw()

    def input(self, key):
        if widgets.help.active:
            widgets.help.input(key)
        elif widgets.cmdline.active:
            widgets.cmdline.input(key)
        elif widgets.menu.active:
            widgets.menu.input(key)
        else:
            widgets.filer.input(key)

    def main_loop(self):
        ui = widget.ui.UI(self.draw, self.input)
        while True:
            ui.run()

    def setup(self, rcpath):
        error = self.loadrcfile(rcpath)
        look.init_colors()
        sysver = sys.version.replace(os.linesep, "")
        widgets.message.puts("Launching on Python {0}".format(sysver))
        if error:
            widgets.message.exception(error)
            widgets.message.error("RC error: instead loaded `{0}'".format(self.environs["RCFILE"]))
        else:
            widgets.message.puts("Loaded {0}".format(self.environs["RCFILE"]))
        widget.refresh_all_widgets()

    def run(self):
        widgets.message.puts("Welcome to pyful v{0}".format(__version__))
        self.init_function()
        try:
            self.main_loop()
        except SystemExit:
            self.exit_function()
