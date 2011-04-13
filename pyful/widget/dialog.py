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
    win = None
    winattr = 0
    messageattr = 0

    def __init__(self, name, register=True):
        base.Widget.__init__(self, name, register)
        self.message = ""
        self.options = []
        self.cursor = 0
        self.y = self.x = self.begy = self.begx = 1
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
        self.win = None
        y, x = self.stdscr.getmaxyx()
        self.y = 2
        self.x = x
        self.begy = y - 2
        self.begx = 0
        self.winattr = look.colors["Window"]
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
        self.active = True

    def hide(self):
        self.win = None
        self.active = False

    def _fix_position(self):
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor >= len(self.options):
            self.cursor = len(self.options) - 1

    def create_window(self):
        if not self.win:
            self.win = curses.newwin(self.y, self.x, self.begy, self.begx)
            self.win.bkgd(self.winattr)

    def view(self):
        self.create_window()
        self._fix_position()

        y, x = self.win.getmaxyx()
        msg = self.message + " "
        try:
            self.win.addstr(self.y_offset, self.x_offset, msg, self.messageattr)
        except curses.error:
            self.win.erase()
            maxwidth = x - 2 - util.termwidth(" ".join(self.options))
            fixed = util.mbs_ljust(msg, maxwidth)
            self.win.addstr(self.y_offset, self.x_offset, fixed, self.messageattr)

        for i, opt in enumerate(self.options):
            if self.cursor == i:
                self.win.addstr(opt, curses.A_REVERSE)
            else:
                self.win.addstr(opt)
            self.win.addstr(" ")
        self.win.move(y-1, x-1)
        self.win.noutrefresh()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
