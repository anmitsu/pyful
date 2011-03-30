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

class Menu(ui.Component):
    keymap = {}
    items = {}

    def __init__(self):
        ui.Component.__init__(self, "Menu")
        self.cursor = 0
        self.win = None
        self.title = None

    def mvcursor(self, x):
        self.cursor += x

    def setcursor(self, x):
        self.cursor = x

    def show(self, name):
        if name not in self.items:
            return message.error("Undefined menu `{0}'".format(name))
        self.title = name
        self.active = self.items[name]
        self.win = curses.newwin(len(self.active)+2, 50, 1, 0)
        self.win.bkgd(look.colors["MenuWindow"])

    def hide(self):
        self.win.erase()
        self.cursor = 0
        self.win = None
        self.active = None

    def run(self):
        swap = self.active
        func = self.active[self.cursor][-1]
        func()
        if self.active is swap:
            self.hide()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            for name, keynum, func in self.active:
                if keynum != key:
                    continue
                swap = self.active
                func()
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

        self.win.border(*self.borders)
        self.win.move(0, 2)
        self.win.addstr(self.title, curses.A_BOLD)

        for i, item in enumerate(items):
            name = util.mbs_ljust(item[0], self.win.getmaxyx()[1]-4)
            if self.cursor == i:
                self.win.move(i+1, 2)
                self.win.addstr(name, curses.A_REVERSE)
            else:
                self.win.move(i+1, 2)
                self.win.addstr(name)
        self.win.noutrefresh()
