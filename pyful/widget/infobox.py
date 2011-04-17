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
import math
import re

from pyful import look
from pyful import util
from pyful.widget import base

class InfoBox(base.Widget):
    scroll_type = "HalfScroll"
    zoom = 0

    def __init__(self, title=None):
        base.Widget.__init__(self, title)
        self.info = []
        self.title = title
        self.cursor = 0
        self.scrolltop = 0
        self.lb = 0
        self.maxrow = 1
        self.keymap = {
            "C-n"   : lambda: self.mvcursor(1),
            "<down>": lambda: self.mvcursor(1),
            "C-v"   : lambda: self.pagedown(),
            "C-d"   : lambda: self.pagedown(),
            "C-p"   : lambda: self.mvcursor(-1),
            "<up>"  : lambda: self.mvcursor(-1),
            "M-n"   : lambda: self.mvscroll(1),
            "M-p"   : lambda: self.mvscroll(-1),
            "M-v"   : lambda: self.pageup(),
            "C-u"   : lambda: self.pageup(),
            "C-g"   : lambda: self.hide(),
            "C-c"   : lambda: self.hide(),
            "ESC"   : lambda: self.hide(),
            "M-+"   : lambda: self.zoombox(+5),
            "M--"   : lambda: self.zoombox(-5),
            "M-="   : lambda: self.zoombox(0),
            }

    def keybind(self, func):
        self.keymap = func(self)
        return self.keymap

    def zoombox(self, amount):
        if amount == 0:
            self.zoom = 0
        else:
            self.zoom += amount
        self.resize()

    def resize(self):
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
        self.panel.resize(height, x, y-height-2, 0)
        self.panel.attr = look.colors["InfoBoxWindow"]

    def show(self, info, pos=None):
        if pos is None:
            pos = self.lb
        self.cursor = pos
        self.scrolltop = 0
        self.info = info
        self.panel.show()

    def hide(self):
        self.cursor = 0
        self.scrolltop = 0
        self.info = []
        self.panel.hide()

    def mvscroll(self, amount):
        if not self.panel.win:
            return
        y, x = self.panel.win.getmaxyx()
        height = (y-2)*self.maxrow
        amount *= self.maxrow
        bottom = self.scrolltop+height
        if amount > 0:
            if bottom >= len(self.info):
                return
            self.scrolltop += amount
            if self.cursor < self.scrolltop:
                self.cursor += amount
        else:
            if self.scrolltop == 0:
                return
            self.scrolltop += amount
            bottom += amount
            if self.cursor >= bottom:
                self.cursor += amount

    def mvcursor(self, amount):
        self.cursor += amount
        if self.cursor < self.lb:
            self.cursor = len(self.info) - 1
        elif self.cursor >= len(self.info):
            self.cursor = 0

    def cursordown(self):
        self.mvcursor(self.maxrow)

    def cursorup(self):
        self.mvcursor(-self.maxrow)

    def setcursor(self, dist):
        if self.lb <= dist < len(self.info):
            self.cursor = dist

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.info) - 1

    def pagedown(self):
        if not self.panel.win:
            return
        height = (self.panel.win.getmaxyx()[0]-2) * self.maxrow
        if self.scrolltop+height >= len(self.info):
            return
        self.scrolltop += height
        self.cursor += height

    def pageup(self):
        if self.scrolltop == 0 or not self.panel.win:
            return
        height = (self.panel.win.getmaxyx()[0]-2) * self.maxrow
        self.scrolltop -= height
        self.cursor -= height

    def cursor_item(self):
        if 0 <= self.cursor < len(self.info):
            return self.info[self.cursor]
        else:
            return Context("")

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()

    def _fix_position(self, size, height, infocount):
        if self.cursor >= size:
            self.cursor = 0
        elif self.cursor < self.lb:
            self.cursor = size - 1

        if self.cursor < self.scrolltop or \
                self.cursor >= self.scrolltop+infocount:
            if self.scroll_type == "HalfScroll":
                self.scrolltop = (self.cursor//self.maxrow*self.maxrow
                                  - height//2*self.maxrow)
            elif self.scroll_type == "PageScroll":
                self.scrolltop = self.cursor//infocount * infocount
            elif self.scroll_type == "ContinuousScroll":
                if self.cursor >= self.scrolltop+infocount:
                    self.scrolltop = (self.cursor//self.maxrow*self.maxrow
                                      + self.maxrow - infocount)
                else:
                    self.scrolltop = self.cursor//self.maxrow*self.maxrow
            else:
                self.scrolltop = self.cursor - height//2*self.maxrow

        if self.scrolltop < 0 or size < height:
            self.scrolltop = 0
        elif self.scrolltop >= size:
            self.scrolltop = size//height * height

    def _draw_titlebar(self, size, infocount):
        if not self.title:
            return
        if self.cursor < 0:
            cpage = 1
        else:
            cpage = self.cursor//infocount + 1
        maxpage = int(math.ceil(float(size)/float(infocount)))
        self.panel.win.addstr(0, 2, "{0}({1}) [{2}/{3}]".format
                               (self.title, size, cpage, maxpage),
                               look.colors["InfoBoxTitle"])

    def _draw_scrollbar(self, size, height, infocount, offset_x):
        if size <= infocount:
            return
        line = 1 + int(float(self.scrolltop) / float(size-infocount) * height)
        if line >= height:
            line = height
        for i in range(1, height+1):
            if i == line:
                self.panel.win.addstr(i, offset_x, "=")
            elif i == 1 or i == height:
                self.panel.win.addstr(i, offset_x, "+")
            else:
                self.panel.win.addstr(i, offset_x, "|")

    def draw(self):
        if not self.info:
            return self.hide()
        self.panel.create_window()

        win = self.panel.win
        size = len(self.info)
        y, x = win.getmaxyx()
        height = y - 2
        width = x - 4
        infowidth = width // self.maxrow
        infocount = height * self.maxrow

        self._fix_position(size, height, infocount)

        win.erase()
        win.border(*self.borders)
        self._draw_titlebar(size, infocount)
        self._draw_scrollbar(size, height, infocount, x-2)

        line = row = 0
        for i in range(self.scrolltop, size):
            if row >= self.maxrow:
                row = 0
                line += 1
                if line >= height:
                    break
            win.move(line+1, row*infowidth+2)
            info = self.info[i]
            if self.cursor == i:
                info.attr += curses.A_REVERSE
                info.addstr(win, infowidth)
                info.attr -= curses.A_REVERSE
            else:
                info.addstr(win, infowidth)
            row += 1
        win.noutrefresh()

class Context(object):
    def __init__(self, string, histr=None, attr=0, hiattr=None):
        if hiattr is None:
            hiattr = look.colors["CandidateHighlight"]
        self.string = string
        self.histr = histr
        self.attr = attr
        self.hiattr = hiattr

    def addstr(self, win, width):
        string = util.mbs_ljust(self.string, width)
        if self.histr:
            r = re.compile(r"({0})".format(re.escape(self.histr)))
            for s in r.split(string):
                if r.match(s):
                    win.addstr(s, self.attr | self.hiattr)
                else:
                    win.addstr(s, self.attr)
        else:
            win.addstr(string, self.attr)
