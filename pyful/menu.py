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

import curses

from pyful import look
from pyful import message
from pyful import ui
from pyful import util
from pyful.keymap import *

class Menu(ui.Component):
    keymap = {}
    _items = {}

    def getitems(self):
        return self.__class__._items
    def setitems(self, itm):
        self.__class__._items.update(itm)
    items = property(getitems, setitems)

    def __init__(self):
        ui.Component.__init__(self, "Menu")
        self.win = None
        self.cursor = 0
        self.title = None

    def mvcursor(self, x):
        self.cursor += x

    def setcursor(self, x):
        self.cursor = x

    def show(self, name):
        if name not in self.items:
            message.error("Undefined menu `%s'" % name)
            return
        self.title = name
        self.active = self._items[name]
        self.win = curses.newwin(len(self.active)+2, 50, 1, 0)
        self.win.bkgdset(" ", look.colors['Window'])

    def hide(self):
        self.win.erase()
        self.cursor = 0
        self.active = None

    def run(self):
        swap = self.active
        value = self.active[self.cursor][-1]
        if hasattr(value, '__call__'):
            value()
        if self.active is swap:
            self.hide()

    def input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
        else:
            for m in self.active:
                if m[1] == key:
                    swap = self.active
                    m[-1]()
                    if swap is self.active:
                        self.hide()
                    break

    def view(self):
        items = self.active
        size = len(items)

        if self.cursor < 0:
            self.cursor = size - 1
        elif not size == 0 and self.cursor >= size:
            self.cursor = 0

        self.win.box()
        self.win.move(0, 2)
        self.win.addstr(self.title, curses.A_BOLD)

        for i, item in enumerate(items):
            title = util.mbs_ljust(item[0], self.win.getmaxyx()[1]-4)
            if self.cursor == i:
                self.win.move(i+1, 2)
                self.win.addstr(title, curses.A_REVERSE)
            else:
                self.win.move(i+1, 2)
                self.win.addstr(title)
        self.win.noutrefresh()
