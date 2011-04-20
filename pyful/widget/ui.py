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

from pyful.widget import base

class UI(object):
    def __init__(self, drawfunc, inputfunc, screen=None):
        self.drawer = Drawer(drawfunc, screen)
        self.controller = Controller(inputfunc, screen)

    def run(self):
        self.drawer.draw_and_update()
        self.controller.control()

class Drawer(object):
    def __init__(self, drawfunc, screen=None):
        self.draw = drawfunc
        if not screen:
            screen = base.StandardScreen.stdscr
        self.screen = screen

    def draw_and_update(self):
        try:
            self.draw()
        except curses.error:
            pass
        curses.setsyx(*self.screen.getmaxyx())
        curses.doupdate()

class Controller(object):
    def __init__(self, inputfunc, screen=None):
        self.input = inputfunc
        self.keyhandler = KeyHandler(screen)

    def control(self):
        key = self.keyhandler.getkey()
        if key != -1:
            if key == "<resize>":
                base.Widget.refresh_all_widgets()
            elif key == "<mouse>":
                # TODO: we have to implement interface of widget for mouse
                pass
            else:
                self.input(key)

class MouseHandler(object):
    buttons = {}

    @classmethod
    def enable(cls, flag):
        if flag:
            attr = curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED
            curses.mousemask(attr)
            curses.mouseinterval(200)
        else:
            curses.mousemask(0)

    def __init__(self):
        pass

    def getmouse(self):
        try:
            return MouseEvent(*curses.getmouse())
        except curses.error:
            pass

class MouseEvent(object):
    def __init__(self, did, x, y, z, bstate):
        self.id = did
        self.y, self.x, self.z = y, x, z
        self.button = MouseHandler.buttons.get(bstate, "ignore")

    def enclose(self, win):
        return win.enclose(self.y, self.x)

    def getrelyx(self, win):
        if self.enclose(win):
            begy, begx = win.getbegyx()
            _y = self.y - begy
            _x = self.x - begx
        else:
            _y = _x = -1
        return (_y, _x)

class KeyHandler(object):
    special_keys = {}
    utf8_skip_data = [1]*192 + [2]*32 + [3]*16 + [4]*8 + [5]*4 + [6]*2 + [1]*2

    def __init__(self, screen=None):
        if screen is None:
            screen = base.StandardScreen.stdscr
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

def _init_special_keys_and_mouse_buttons():
    for name in dir(curses):
        if name.startswith("KEY_"):
            keyname = "<{0}>".format(name[4:].lower())
            KeyHandler.special_keys[getattr(curses, name)] = keyname
        elif name.startswith("BUTTON"):
            MouseHandler.buttons[getattr(curses, name)] = name
_init_special_keys_and_mouse_buttons()
