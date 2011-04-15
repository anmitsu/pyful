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
from pyful import util
from pyful.widget import base

class DialogBox(base.Widget):
    messageattr = 0

    def __init__(self, name, register=True):
        base.Widget.__init__(self, name, register)
        self.message = ""
        self.options = []
        self.cursor = 0
        self.y_offset = 0
        self.x_offset = 1
        self.keymap = {
            "C-f"     : lambda: self.mvcursor(1),
            "<right>" : lambda: self.mvcursor(1),
            "C-b"     : lambda: self.mvcursor(-1),
            "<left>"  : lambda: self.mvcursor(-1),
            "C-a"     : lambda: self.settop(),
            "C-e"     : lambda: self.setbottom(),
            "C-c"     : lambda: self.hide(),
            "C-g"     : lambda: self.hide(),
            "ESC"     : lambda: self.hide(),
            }

    def keybind(self, func):
        self.keymap = func(self)
        return self.keymap

    def resize(self):
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(2, x, y-2, 0)
        self.panel.attr = look.colors["Window"]
        self.messageattr = 0

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.options) - 1

    def mvcursor(self, amount):
        self.cursor += amount

    def setcursor(self, dist):
        self.cursor = dist

    def cursor_item(self):
        return self.options[self.cursor]

    def show(self, message, options):
        self.message = message
        self.options = options
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def _fix_position(self):
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor >= len(self.options):
            self.cursor = len(self.options) - 1

    def draw(self):
        self.panel.create_window()
        win = self.panel.win
        self._fix_position()

        win.erase()
        y, x = win.getmaxyx()
        msg = self.message + " "
        try:
            win.addstr(self.y_offset, self.x_offset, msg, self.messageattr)
        except curses.error:
            win.erase()
            maxwidth = x - 2 - util.termwidth(" ".join(self.options))
            fixed = util.mbs_ljust(msg, maxwidth)
            win.addstr(self.y_offset, self.x_offset, fixed, self.messageattr)

        for i, opt in enumerate(self.options):
            if self.cursor == i:
                win.addstr(opt, curses.A_REVERSE)
            else:
                win.addstr(opt)
            win.addstr(" ")
        win.noutrefresh()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
