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
import signal

from pyful import look
from pyful import util
from pyful.keymap import *

def getcomponent(name):
    return Component.components[name]

def getch():
    meta = False
    while True:
        key = StandardScreen.stdscr.getch()
        if meta:
            if key == 27:
                return (False, key)
            return (True, key)
        if key == 27:
            meta = True
        else:
            return (False, key)

def zoom_infobox(zoom):
    InfoBox.zoom = zoom
    InfoBox.resize()

def setbox(*boxtable):
    pass

def resize():
    getcomponent("Cmdscr").resize()
    getcomponent("Titlebar").resize()
    getcomponent("Filer").workspace.resize()
    getcomponent("MessageBox").resize()
    InfoBox.resize()

def refresh(*args):
    curses.endwin()
    StandardScreen.stdscr.refresh()
    resize()

def start_curses():
    signal.signal(signal.SIGWINCH, refresh)
    try:
        curses.noecho()
        curses.cbreak()
        curses.raw()
    except curses.error:
        StandardScreen()
        CmdlineScreen()
        Titlebar()
        InfoBox.resize()
        getcomponent("MessageBox").resize()
        getcomponent("Filer").default_init()
        StandardScreen.stdscr.refresh()

def end_curses():
    signal.signal(signal.SIGWINCH, signal.SIG_DFL)
    StandardScreen.destroy()

class ComponentDuplication(Exception):
    pass

class StandardScreen(object):
    stdscr = None
    borders = []

    def __init__(self):
        if not self.stdscr:
            self.__class__.stdscr = curses.initscr()
            self.stdscr.notimeout(0)
            self.stdscr.keypad(1)
            curses.noecho()
            curses.cbreak()
            curses.raw()
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
            look.init_colors()

    @classmethod
    def destroy(cls):
        if cls.stdscr:
            curses.echo()
            curses.nocbreak()
            curses.noraw()
            curses.endwin()

class Component(StandardScreen):
    components = {}

    def __init__(self, name):
        self.active = False
        if not name in self.components:
            self.components[name] = self
        else:
            raise ComponentDuplication("`{0}' overlap for components".format(name))

    @property
    def is_active(self):
        return self.active

class CmdlineScreen(Component):
    def __init__(self):
        Component.__init__(self, "Cmdscr")
        y, x = self.stdscr.getmaxyx()
        self.win = curses.newwin(2, x, y-2, 0)
        self.win.bkgd(look.colors["CmdlineWindow"])

    def resize(self):
        (y, x) = self.stdscr.getmaxyx()
        self.win = curses.newwin(2, x, y-2, 0)
        self.win.bkgd(look.colors["CmdlineWindow"])

class Titlebar(Component):
    def __init__(self):
        Component.__init__(self, "Titlebar")
        (y, x) = self.stdscr.getmaxyx()
        self.win = curses.newwin(1, x, 0, 0)
        self.win.bkgd(look.colors["Titlebar"])

    def resize(self):
        (y, x) = self.stdscr.getmaxyx()
        self.win = curses.newwin(1, x, 0, 0)
        self.win.bkgd(look.colors["Titlebar"])

class InfoBox(Component):
    scroll_type = "HalfScroll"
    zoom = 0
    win = None

    def __init__(self, title):
        Component.__init__(self, title)
        self.info = []
        self.title = title
        self.cursor = 0
        self.scrolltop = 0
        self.maxrow = 1
        self.keymap = {
            (0, KEY_CTRL_N): lambda: self.mvcursor(1),
            (0, KEY_DOWN  ): lambda: self.mvcursor(1),
            (0, KEY_CTRL_V): lambda: self.pagedown(),
            (0, KEY_CTRL_D): lambda: self.pagedown(),
            (0, KEY_CTRL_P): lambda: self.mvcursor(-1),
            (0, KEY_UP    ): lambda: self.mvcursor(-1),
            (1, KEY_n     ): lambda: self.mvscroll(1),
            (1, KEY_p     ): lambda: self.mvscroll(-1),
            (1, KEY_v     ): lambda: self.pageup(),
            (0, KEY_CTRL_U): lambda: self.pageup(),
            (0, KEY_CTRL_G): lambda: self.hide(),
            (0, KEY_CTRL_C): lambda: self.hide(),
            (0, KEY_ESCAPE): lambda: self.hide(),
            (1, KEY_PLUS  ): lambda: zoom_infobox(InfoBox.zoom+5),
            (1, KEY_MINUS ): lambda: zoom_infobox(InfoBox.zoom-5),
            (1, KEY_EQUAL ): lambda: zoom_infobox(0),
            }

    @classmethod
    def resize(cls):
        y, x = cls.stdscr.getmaxyx()
        odd = y % 2
        base = y//2 + odd
        height = base + cls.zoom
        if height > y-2:
            height = y - 2
            cls.zoom = height - base
        elif height < 3:
            height = 3
            cls.zoom = height - base - 2
        cls.win = curses.newwin(height, x, y-height-2, 0)
        cls.win.bkgd(look.colors["InfoBoxWindow"])

    def show(self, info, pos=0):
        self.active = True
        self.cursor = pos
        self.scrolltop = 0
        self.info = info

    def hide(self):
        self.win.erase()
        self.active = False
        self.cursor = 0
        self.scrolltop = 0
        self.info = []

    def mvscroll(self, amount):
        y, x = self.win.getmaxyx()
        height = (y-2)*self.maxrow
        amount *= self.maxrow
        bottom = self.scrolltop+height
        if amount > 0:
            if bottom >= len(self.info):
                return
            self.scrolltop += amount
            if self.cursor < self.scrolltop:
                self.cursor = self.scrolltop
        else:
            if self.scrolltop == 0:
                return
            self.scrolltop += amount
            bottom += amount
            if self.cursor >= bottom:
                self.cursor = bottom - 1

    def mvcursor(self, amount):
        self.cursor += amount
        if self.cursor < -1:
            self.cursor = len(self.info) - 1
        elif self.cursor >= len(self.info):
            self.cursor = 0

    def cursordown(self):
        self.mvcursor(self.maxrow)

    def cursorup(self):
        self.mvcursor(-self.maxrow)

    def setcursor(self, dist):
        if -1 <= dist < len(self.info):
            self.cursor = dist

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.info) - 1

    def pagedown(self):
        height = (self.win.getmaxyx()[0]-2) * self.maxrow
        if self.scrolltop+height >= len(self.info):
            return
        self.scrolltop += height
        self.cursor += height

    def pageup(self):
        if self.scrolltop == 0:
            return
        height = (self.win.getmaxyx()[0]-2) * self.maxrow
        self.scrolltop -= height
        self.cursor -= height

    def cursor_item(self):
        if 0 <= self.cursor < len(self.info):
            return self.info[self.cursor]
        else:
            return InfoBoxContext("")

    def input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()

    def _revise_position(self, size, height, infocount):
        if self.cursor >= size:
            self.cursor = 0
        elif self.cursor < -1:
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

    def _view_titlebar(self, size, infocount):
        self.win.move(0, 2)
        if self.cursor < 0:
            cpage = 1
        else:
            cpage = (self.cursor)//infocount+1
        maxpage = size//infocount+1
        self.win.addstr("{0}({1}) [{2}/{3}]".format
                        (self.title, size, cpage, maxpage),
                        look.colors["InfoBoxTitle"])

    def view(self):
        if not self.info:
            return self.hide()

        size = len(self.info)
        y, x = self.win.getmaxyx()
        height = y - 2
        width = x - 3
        infowidth = width // self.maxrow
        infocount = height * self.maxrow

        self._revise_position(size, height, infocount)

        self.win.erase()
        self.win.border(*self.borders)
        self._view_titlebar(size, infocount)

        line = row = 0
        for i in range(self.scrolltop, size):
            if row >= self.maxrow:
                row = 0
                line += 1
                if line >= height:
                    break
            self.win.move(line+1, row*infowidth+2)
            info = self.info[i]
            if self.cursor == i:
                info.attr += curses.A_REVERSE
                info.addstr(self.win, infowidth)
                info.attr -= curses.A_REVERSE
            else:
                info.addstr(self.win, infowidth)
            row += 1
        self.win.noutrefresh()

class InfoBoxContext(object):
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
