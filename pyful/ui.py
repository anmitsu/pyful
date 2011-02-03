# ui.py - user interface
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
import re

from pyful import util
from pyful import look
from pyful.keymap import *

def init_ui():
    InfoBox.resize()

def zoom_infobox(zoom):
    InfoBox.zoom = zoom
    InfoBox.resize()

class InfoBox(object):
    win = None
    zoom = 0

    def __init__(self, title):
        self._title = title
        self._info = None

        self._highlight = None
        self._cursor = 0
        self._scrolltop = 0
        self._active = False
        self.keymap = {
            (0, KEY_CTRL_N): lambda: self.mvcursor(1),
            (0, KEY_DOWN  ): lambda: self.mvcursor(1),
            (0, KEY_CTRL_V): lambda: self.pagedown(),
            (0, KEY_CTRL_D): lambda: self.pagedown(),
            (0, KEY_CTRL_P): lambda: self.mvcursor(-1),
            (0, KEY_UP    ): lambda: self.mvcursor(-1),
            (1, KEY_v     ): lambda: self.pageup(),
            (0, KEY_CTRL_U): lambda: self.pageup(),
            (0, KEY_CTRL_G): lambda: self.hide(),
            (0, KEY_CTRL_C): lambda: self.hide(),
            (0, KEY_ESCAPE): lambda: self.hide(),
            }

    @classmethod
    def resize(cls):
        from pyful import Pyful
        core = Pyful()
        odd = core.stdscr.maxy % 2
        base = core.stdscr.maxy//2 + odd
        height = base + cls.zoom
        if height > core.stdscr.maxy-2:
            height = core.stdscr.maxy - 2
            cls.zoom = height - base
        elif height < 3:
            height = 3
            cls.zoom = height - base - 2
        cls.win = curses.newwin(height, core.stdscr.maxx, core.stdscr.maxy-height-2, 0)

    @property
    def info(self):
        return self._info

    @property
    def cursor(self):
        return self._cursor

    @property
    def active(self):
        return self._active

    def show(self, info, pos=0, highlight=None):
        self.win.erase()
        self._cursor = pos
        self._scrolltop = 0
        self._active = True
        self._highlight = highlight
        self._info = info

    def hide(self):
        self._cursor = 0
        self._scrolltop = 0
        self._active = False
        self._highlight = None
        self._info = None

    def mvcursor(self, x):
        if not self._info:
            return
        self._cursor += x

        size = len(self._info)
        if self._cursor >= size:
            self._cursor = 0
        elif self._cursor < -1:
            self._cursor = size - 1

    def setcursor(self, x):
        if not self._info:
            return
        self._cursor = x

        size = len(self._info)
        if self._cursor >= size:
            self._cursor = 0
        elif self._cursor < -1:
            self._cursor = size - 1

    def settop(self):
        self._cursor = 0

    def setbottom(self):
        if self._info:
            self._cursor = len(self._info) - 1

    def pagedown(self):
        self._cursor += self.win.getmaxyx()[0] - 2

    def pageup(self):
        self._cursor -= self.win.getmaxyx()[0] - 2

    def cursor_item(self):
        if self._info:
            return self._info[self._cursor]

    def input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()

    def view(self, maxrow=1):
        if not self._info:
            return self.hide()

        size = len(self._info)
        maxxy = self.win.getmaxyx()
        height = maxxy[0] - 2
        width = maxxy[1] - 2
        row = 0

        if self._cursor >= size:
            self._cursor = 0
        elif self._cursor < -1:
            self._cursor = size - 1

        if (self._cursor < self._scrolltop or self._cursor > self._scrolltop + ((height-1)*maxrow)) and not self._cursor == -1:
            self._scrolltop = (self._cursor//(height*maxrow)) * (height*maxrow)
            if self._scrolltop < 0:
                self._scrolltop = 0
            self.win.erase()

        self.win.box()
        self.win.move(0, 2)
        if self._cursor <= -1:
            current_page = 1
        else:
            current_page = self._cursor//(height*maxrow)+1
        max_page = (size-1)//(height*maxrow)+1
        self.win.addstr("%s(%d) [%d/%d]" %
                        (self._title, size, current_page, max_page),
                        curses.A_BOLD | curses.A_UNDERLINE)

        line = 0
        for i in range(self._scrolltop, size):
            if row >= maxrow:
                row = 0
                line += 1
            if line >= height:
                break

            item = util.mbs_ljust(self._info[i], width//maxrow - 3)
            self.win.move(line+1, row * (width//maxrow) + 2)
            if self._cursor == i:
                self.win.addstr(item, curses.A_REVERSE)
            else:
                if self._highlight:
                    reg = re.compile("(%s)" % re.escape(self._highlight))
                    for iitem in reg.split(item):
                        if iitem == self._highlight:
                            self.win.addstr(iitem, look.colors['CANDIDATE_HILIGHT'])
                        else:
                            self.win.addstr(iitem)
                else:
                    self.win.addstr(item)
            row += 1
        self.win.noutrefresh()

class ContextBox(object):
    def __init__(self):
        self.win = None
        self._cursor = 0
        self._scrolltop = 0
        self._active = 0
        self._contents = None
        self.keymap = {}

    def input (self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()

    def view(self):
        pass
