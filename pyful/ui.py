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

from pyful import widget

def refresh():
    curses.endwin()
    widget.base.StandardScreen.stdscr.refresh()
    widget.resize()

def start_widget():
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
        widget.base.StandardScreen()

def end_curses():
    widget.base.StandardScreen.destroy()

class Drawer(object):
    def __init__(self, drawfunc=None):
        if drawfunc is None:
            drawfunc = self._get_default_draw_function()
        self.draw = drawfunc
        self.stdscr = widget.base.StandardScreen.stdscr

    def _get_default_draw_function(self):
        filer = widget.get("Filer")
        menu = widget.get("Menu")
        cmdline = widget.get("Cmdline")
        helper = widget.get("Help")
        message = widget.get("Message")
        def drawfunc():
            filer.draw()
            if menu.active:
                menu.draw()
            if helper.active:
                helper.draw()
            elif cmdline.active:
                cmdline.draw()
            elif message.active and not filer.finder.active:
                message.draw()
        return drawfunc

    def draw_and_update(self):
        self.draw()
        curses.setsyx(*self.stdscr.getmaxyx())
        curses.doupdate()

class Controller(object):
    def __init__(self, inputfunc=None):
        if inputfunc is None:
            inputfunc = self._get_default_input_function()
        self.input = inputfunc
        self.keyhandler = KeyHandler()

    def _get_default_input_function(self):
        filer = widget.get("Filer")
        menu = widget.get("Menu")
        cmdline = widget.get("Cmdline")
        helper = widget.get("Help")
        def inputfunc(key):
            if helper.active:
                helper.input(key)
            elif cmdline.active:
                cmdline.input(key)
            elif menu.active:
                menu.input(key)
            else:
                filer.input(key)
        return inputfunc

    def control(self):
        key = self.keyhandler.getkey()
        if key != -1:
            if key == "<resize>":
                refresh()
            else:
                self.input(key)

class KeyHandler(object):
    special_keys = {}
    utf8_skip_data = [1]*192 + [2]*32 + [3]*16 + [4]*8 + [5]*4 + [6]*2 + [1]*2

    def __init__(self, screen=None):
        if screen is None:
            screen = widget.base.StandardScreen.stdscr
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
            KeyHandler.special_keys[getattr(curses, name)] = keyname

_init_special_keys()
