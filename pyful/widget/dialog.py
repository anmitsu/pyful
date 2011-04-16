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

class Dialog(base.Widget):
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

    def resize(self):
        pass

    def draw(self):
        pass

    def input(self, key):
        pass

    def show(self, message, options):
        self.message = message
        self.options = options
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def keybind(self, func):
        self.keymap = func(self)
        return self.keymap

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

    def fix_position(self):
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor >= len(self.options):
            self.cursor = len(self.options) - 1

class DialogBar(Dialog):
    def __init__(self, name, register=True):
        Dialog.__init__(self, name, register)

    def show(self, message, options):
        self.message = message
        self.options = options
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def resize(self):
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(2, x, y-2, 0)
        self.panel.attr = look.colors["Window"]
        self.messageattr = look.colors["ConfirmMessage"]

    def draw(self):
        self.panel.create_window()
        win = self.panel.win
        self.fix_position()

        win.erase()
        y, x = win.getmaxyx()
        y_offset = 0
        x_offset = 1
        msg = self.message + " "
        try:
            win.addstr(y_offset, x_offset, msg, self.messageattr)
        except curses.error:
            win.erase()
            maxwidth = x - 2 - util.termwidth(" ".join(self.options))
            fixed = util.mbs_ljust(msg, maxwidth)
            win.addstr(y_offset, x_offset, fixed, self.messageattr)

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

class DialogBox(Dialog):
    def __init__(self, name, register=True):
        Dialog.__init__(self, name, register)

    def resize(self):
        self.messageattr = look.colors["ConfirmMessage"]

    def show(self, message, options):
        self.lines = message.splitlines()
        self.options = options
        self.panel.resize(*self.get_window_size())
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def get_window_size(self):
        olen = util.termwidth(" ".join(self.options))
        mlen = max(util.termwidth(line) for line in self.lines)
        height = len(self.lines) + 4
        width = max(mlen, olen) + 4

        y, x = self.stdscr.getmaxyx()
        if height > y:
            height = y
        if width > x:
            width = x
        begy = y//2 - height//2
        begx = x//2 - width//2
        if begy < 0:
            begy = 0
        if begx < 0:
            begx = 0
        return (height, width, begy, begx)

    def draw(self):
        self.panel.create_window()
        win = self.panel.win
        y, x = win.getmaxyx()
        win.erase()
        win.border(*self.borders)
        self.fix_position()

        for i, line in enumerate(range(1, 1+len(self.lines))):
            if line >= y-2:
                break
            try:
                win.addstr(line, 2, self.lines[i])
            except curses.error:
                break

        olen = util.termwidth(" ".join(self.options))
        if olen > x-2:
            win.move(y-2, 2)
        else:
            win.move(y-2, (x-olen)//2)
        for i, opt in enumerate(self.options):
            if self.cursor == i:
                win.addstr(opt, curses.A_REVERSE)
            else:
                win.addstr(opt)
            win.addstr(" ")
        win.noutrefresh()
