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

import array
import curses
import math
import re
import signal

from pyful import look
from pyful import util

def getcomponent(name):
    return Component.components[name]

def resize():
    for component in Component.components.values():
        component.resize()

def refresh(*args):
    curses.endwin()
    StandardScreen.stdscr.refresh()
    resize()

def start_ui():
    import pyful.cmdline
    import pyful.filer
    import pyful.message
    import pyful.menu
    import pyful.help
    pyful.cmdline.Cmdline()
    pyful.filer.Filer()
    pyful.message.Message()
    pyful.menu.Menu()
    pyful.help.Help()

def start_curses():
    try:
        curses.noecho()
        curses.cbreak()
        curses.raw()
    except curses.error:
        StandardScreen()
        CmdlineScreen()
        Titlebar()
    signal.signal(signal.SIGWINCH, refresh)

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
            curses.nonl()
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
            look.init_colors()
            self.stdscr.refresh()

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

    def resize(self):
        pass

class CmdlineScreen(Component):
    def __init__(self):
        Component.__init__(self, "Cmdscr")
        y, x = self.stdscr.getmaxyx()
        self.win = curses.newwin(2, x, y-2, 0)
        self.win.bkgd(look.colors["CmdlineWindow"])

    def resize(self):
        y, x = self.stdscr.getmaxyx()
        self.win = curses.newwin(2, x, y-2, 0)
        self.win.bkgd(look.colors["CmdlineWindow"])

class Titlebar(Component):
    def __init__(self):
        Component.__init__(self, "Titlebar")
        y, x = self.stdscr.getmaxyx()
        self.win = curses.newwin(1, x, 0, 0)
        self.win.bkgd(look.colors["Titlebar"])

    def resize(self):
        y, x = self.stdscr.getmaxyx()
        self.win = curses.newwin(1, x, 0, 0)
        self.win.bkgd(look.colors["Titlebar"])

class InfoBox(Component):
    scroll_type = "HalfScroll"
    zoom = 0
    win = None
    winattr = 0

    def __init__(self, title):
        Component.__init__(self, title)
        self.info = []
        self.title = title
        self.cursor = 0
        self.scrolltop = 0
        self.maxrow = 1
        self.y = self.x = self.begy = self.begx = 1
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

    def zoombox(self, amount):
        if amount == 0:
            self.zoom = 0
        else:
            self.zoom += amount
        self.resize()

    def resize(self):
        self.win = None
        y, x = self.stdscr.getmaxyx()
        odd = y % 2
        base = y//2 + odd
        height = base + self.zoom
        if height > y-2:
            height = y - 2
            self.zoom = height - base
        elif height < 3:
            height = 3
            self.zoom = height - base
        self.y = height
        self.x = x
        self.begy = y-height-2
        self.begx = 0
        self.winattr = look.colors["InfoBoxWindow"]

    def show(self, info, pos=0):
        self.active = True
        self.cursor = pos
        self.scrolltop = 0
        self.info = info

    def hide(self):
        self.win = None
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

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()

    def _fix_position(self, size, height, infocount):
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
        if self.cursor < 0:
            cpage = 1
        else:
            cpage = self.cursor//infocount + 1
        maxpage = int(math.ceil(float(size)/float(infocount)))
        self.win.addstr(0, 2, "{0}({1}) [{2}/{3}]".format
                        (self.title, size, cpage, maxpage),
                        look.colors["InfoBoxTitle"])

    def create_window(self):
        if not self.win:
            self.win = curses.newwin(self.y, self.x, self.begy, self.begx)
            self.win.bkgd(self.winattr)

    def view(self):
        if not self.info:
            return self.hide()
        self.create_window()

        size = len(self.info)
        y, x = self.win.getmaxyx()
        height = y - 2
        width = x - 4
        infowidth = width // self.maxrow
        infocount = height * self.maxrow

        self._fix_position(size, height, infocount)

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

class Viewer(object):
    def __init__(self, viewfunc=None):
        if viewfunc is None:
            viewfunc = self._get_default_view_function()
        self.view = viewfunc

    def _get_default_view_function(self):
        filer = getcomponent("Filer")
        menu = getcomponent("Menu")
        cmdline = getcomponent("Cmdline")
        helper = getcomponent("Help")
        message = getcomponent("Message")
        def viewfunc():
            filer.view()
            if menu.is_active:
                menu.view()
            if helper.is_active:
                helper.view()
            elif cmdline.is_active:
                cmdline.view()
            elif message.is_active:
                message.view()
        return viewfunc

    def view_and_update(self):
        self.view()
        curses.doupdate()

class Controller(object):
    def __init__(self, inputfunc=None):
        if inputfunc is None:
            inputfunc = self._get_default_input_function()
        self.input = inputfunc
        self.keyhandler = KeyHandler()

    def _get_default_input_function(self):
        filer = getcomponent("Filer")
        menu = getcomponent("Menu")
        cmdline = getcomponent("Cmdline")
        helper = getcomponent("Help")
        def inputfunc(key):
            if helper.is_active:
                helper.input(key)
            elif cmdline.is_active:
                cmdline.input(key)
            elif menu.is_active:
                menu.input(key)
            else:
                filer.input(key)
        return inputfunc

    def control(self):
        key = self.keyhandler.getkey()
        if key != -1:
            self.input(key)

class KeyHandler(object):
    special_keys = {}
    utf8_skip_data = [1]*192 + [2]*32 + [3]*16 + [4]*8 + [5]*4 + [6]*2 + [1]*2

    def __init__(self, screen=None):
        if screen is None:
            screen = StandardScreen.stdscr
        self.screen = screen

    def getkey(self):
        ch = self.screen.getch()
        if ch == -1:
            return -1
        elif ch & 0xc0 == 0xc0: # Is ch utf8 muliti byte character?
            buf = array.array("B", [ch])
            buf.extend(self.screen.getch() for i in range(1, self.utf8_skip_data[ch]))
            key = buf.tostring().decode()
        else:
            key = self._get_key_for(ch)
        return key

    def _get_key_for(self, ch, escaped=False):
        key = -1
        if ch == 27:
            if escaped:
                key = "ESC"
            else:
                key = self._get_key_for(self.screen.getch(), escaped=True)
                if key != "ESC":
                    key = "M-" + key
        elif ch == 13:
            key = "RET"
        elif ch == 32:
            key = "SPC"
        elif 32 < ch <= 126:
            key = chr(ch)
        elif ch in self.special_keys:
            key = self.special_keys[ch]
        elif 0 <= ch < 32:
            if ch == 0:
                key = "C-SPC"
            elif 0 < ch < 27:
                key = "C-" + chr(ch + 96)
            else:
                key = "UNKNOWN ({0:d} :: 0x{0:x})".format(ch)
        return key

def _init_special_keys():
    for name in dir(curses):
        if name.startswith("KEY_"):
            keyname = "<{0}>".format(name[4:].lower())
            KeyHandler.special_keys[curses.__dict__[name]] = keyname

_init_special_keys()
