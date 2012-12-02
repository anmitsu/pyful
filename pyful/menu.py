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

from pyful.widget.listbox import ListBox, Entry

def define_menu(name, items):
    Menu.items[name] = items

class Menu(ListBox):
    items = {}

    def __init__(self):
        ListBox.__init__(self, "Menu")
        self.title = ""
        self.current = None

    def show(self, name, pos=0):
        if name not in self.items:
            return message.error("Undefined menu `{0}'".format(name))
        self.title = name
        self.current = self.items[name]
        self.refresh()
        entries = [Entry("{0} ({1})".format(item[0], item[1])) for item in self.current]
        super(self.__class__, self).show(entries, pos)

    def hide(self):
        self.current = None
        super(self.__class__, self).hide()

    def refresh(self):
        y, x = self.stdscr.getmaxyx()
        odd = y % 2
        base_y = y//2 + odd
        height = base_y + self.zoom
        if height > y-2:
            height = y - 2
            self.zoom = height - base_y
        elif height < 3:
            height = 3
            self.zoom = height - base_y
        width = x // 3
        self.panel.resize(height, width, y-height-3, 0)
        self.panel.attr = look.colors["MenuWindow"]

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
            except ValueError:
                pass
