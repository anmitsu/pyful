# menu.py - menu management
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

from pyful import look
from pyful import message
from pyful import ui

class Menu(ui.InfoBox):
    items = {}

    def __init__(self):
        ui.InfoBox.__init__(self, "Menu")
        self.title = ""
        self.current = None

    def show(self, name, pos=0):
        if name not in self.items:
            return message.error("Undefined menu `{0}'".format(name))
        self.title = name
        self.current = self.items[name]
        self.resize()
        info = [ui.InfoBoxContext(i[0]) for i in self.current]
        super(self.__class__, self).show(info, pos)

    def hide(self):
        self.current = None
        super(self.__class__, self).hide()

    def resize(self):
        if not self.current:
            return
        self.win = None
        y, x = self.stdscr.getmaxyx()
        maxy = y // 2
        height = len(self.current) + 2
        if height > maxy:
            height = maxy
        width = 50
        if width > x:
            width = x
        self.y = height
        self.x = width
        self.begy = 1
        self.begx = 0
        self.winattr = look.colors["MenuWindow"]

    def run(self):
        swap = self.current
        func = self.current[self.cursor][-1]
        func()
        if self.current is swap:
            self.hide()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            swap = self.current
            names, keys, funcs = zip(*self.current)
            try:
                funcs[keys.index(key)]()
                if swap is self.current:
                    self.hide()
            except IndexError:
                pass
