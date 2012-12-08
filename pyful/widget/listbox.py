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

from pyful.widget.base import Widget

class ListBox(Widget):
    scroll_type = "HalfScroll"
    zoom = 0
    keymap = None

    def __init__(self, title=None):
        Widget.__init__(self, title)
        self.list = []
        self.title = title
        self.cursor = 0
        self.scrolltop = 0
        self.lb = 0
        self.maxrow = 1

    def zoombox(self, amount):
        if amount == 0:
            self.zoom = 0
        else:
            self.zoom += amount
        self.refresh()

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
        self.panel.resize(height, x, y-height-2, 0)
        self.panel.attr = look.colors["ListBoxWindow"]

    def show(self, entries, pos=None):
        if pos is None:
            pos = self.lb
        self.cursor = pos
        self.scrolltop = 0
        self.list = entries
        self.panel.show()

    def hide(self):
        self.cursor = 0
        self.scrolltop = 0
        self.list = []
        self.panel.hide()

    def mvscroll(self, amount):
        if not self.panel.win:
            return
        y, x = self.panel.win.getmaxyx()
        height = (y-2)*self.maxrow
        amount *= self.maxrow
        bottom = self.scrolltop+height
        if amount > 0:
            if bottom >= len(self.list):
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
            self.cursor = len(self.list) - 1
        elif self.cursor >= len(self.list):
            self.cursor = 0

    def cursordown(self):
        self.mvcursor(self.maxrow)

    def cursorup(self):
        self.mvcursor(-self.maxrow)

    def setcursor(self, dist):
        if self.lb <= dist < len(self.list):
            self.cursor = dist

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.list) - 1

    def pagedown(self):
        if not self.panel.win:
            return
        height = (self.panel.win.getmaxyx()[0]-2) * self.maxrow
        if self.scrolltop+height >= len(self.list):
            return
        self.scrolltop += height
        self.cursor += height

    def pageup(self):
        if self.scrolltop == 0 or not self.panel.win:
            return
        height = (self.panel.win.getmaxyx()[0]-2) * self.maxrow
        self.scrolltop -= height
        self.cursor -= height

    def cursor_entry(self):
        if 0 <= self.cursor < len(self.list):
            return self.list[self.cursor]
        else:
            return Entry("")

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()

    def _fix_position(self, size, height, listcount):
        if self.cursor >= size:
            self.cursor = 0
        elif self.cursor < self.lb:
            self.cursor = size - 1

        if self.cursor < self.scrolltop or \
                self.cursor >= self.scrolltop+listcount:
            if self.scroll_type == "HalfScroll":
                self.scrolltop = (self.cursor//self.maxrow*self.maxrow
                                  - height//2*self.maxrow)
            elif self.scroll_type == "PageScroll":
                self.scrolltop = self.cursor//listcount * listcount
            elif self.scroll_type == "ContinuousScroll":
                if self.cursor >= self.scrolltop+listcount:
                    self.scrolltop = (self.cursor//self.maxrow*self.maxrow
                                      + self.maxrow - listcount)
                else:
                    self.scrolltop = self.cursor//self.maxrow*self.maxrow
            else:
                self.scrolltop = self.cursor - height//2*self.maxrow

        if self.scrolltop < 0 or size < height:
            self.scrolltop = 0
        elif self.scrolltop >= size:
            self.scrolltop = size//height * height

    def _draw_titlebar(self, win, size, listcount):
        if not self.title:
            return
        if self.cursor < 0:
            cpage = 1
        else:
            cpage = self.cursor//listcount + 1
        maxpage = int(math.ceil(float(size)/float(listcount)))
        win.addstr(0, 2, "{0}({1}) [{2}/{3}]".format
                   (self.title, size, cpage, maxpage),
                   look.colors["ListBoxTitle"])

    def _draw_scrollbar(self, win, size, height, listcount, x_offset):
        if size <= listcount:
            return
        line = 1 + int(float(self.scrolltop) / float(size-listcount) * height)
        if line >= height:
            line = height
        for i in range(1, height+1):
            if i == line:
                win.addstr(i, x_offset, "=")
            elif i == 1 or i == height:
                win.addstr(i, x_offset, "+")
            else:
                win.addstr(i, x_offset, "|")

    def draw(self):
        if not self.list:
            return
        self.panel.create_window()
        win = self.panel.win
        size = len(self.list)
        y, x = win.getmaxyx()
        height = y - 2
        width = x - 4
        listwidth = width // self.maxrow
        listcount = height * self.maxrow

        self._fix_position(size, height, listcount)

        win.erase()
        win.border(*self.borders)
        self._draw_titlebar(win, size, listcount)
        self._draw_scrollbar(win, size, height, listcount, x-2)

        line = row = 0
        for i in range(self.scrolltop, size):
            if row >= self.maxrow:
                row = 0
                line += 1
                if line >= height:
                    break
            win.move(line+1, row*listwidth+2)
            entry = self.list[i]
            if self.cursor == i:
                entry.attr += curses.A_REVERSE
                entry.addstr(win, listwidth)
                entry.attr -= curses.A_REVERSE
            else:
                entry.addstr(win, listwidth)
            row += 1
        win.noutrefresh()

class Entry(object):
    __slots__ = ["text", "histr", "attr", "hiattr"]

    def __init__(self, text, histr=None, attr=0, hiattr=None):
        if hiattr is None:
            hiattr = look.colors["CandidateHighlight"]
        self.text = text
        self.histr = histr
        self.attr = attr
        self.hiattr = hiattr

    def addstr(self, win, width):
        text = util.mbs_ljust(self.text, width)
        self.addtext(win, text)

    def addtext(self, win, text):
        if self.histr:
            r = re.compile(r"({0})".format(re.escape(self.histr)))
            for s in r.split(text):
                if r.match(s):
                    win.addstr(s, self.attr | self.hiattr)
                else:
                    win.addstr(s, self.attr)
        else:
            win.addstr(text, self.attr)
