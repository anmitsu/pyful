# message.py - message management
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
from threading import Timer

from pyful import Pyful
from pyful import Singleton
from pyful import look
from pyful import ui
from pyful.keymap import *

class Message(Singleton):
    def __init_of_singleton__(self):
        self.msg = ""
        self.type = "puts"
        self.active = False
        self.timer = None
        self.core = Pyful()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(timex, self.hide)
        self.timer.start()

    def puts(self, string, timex=4):
        self.active = True
        self.msg = string
        self.type = "puts"
        self.view()
        self.start_timer(timex)

    def error(self, string, timex=4):
        self.active = True
        self.msg = string
        self.type = "error"
        self.view()
        self.start_timer(timex)

    def exception(self, except_cls):
        self.error('%s: %s' % (except_cls.__class__.__name__, str(except_cls)))

    def confirm(self, msg, options, msglist=None, position=0):
        self.active = True
        self.core.view()
        cnf = Confirm(msg, options, msglist)
        cnf.setcursor(position)
        while cnf.active:
            cnf.view()
            (meta, key) = self.core.stdscr.getch()
            cnf.input(meta, key)
        self.active = False
        return cnf.result

    def hide(self):
        self.msg = ""
        self.active = False
        self.core.stdscr.cmdwin.erase()
        self.core.stdscr.cmdwin.noutrefresh()
        self.core.view()

    def view(self):
        self.core.stdscr.cmdwin.erase()
        self.core.stdscr.cmdwin.move(0, 1)

        if self.type == "puts":
            self.core.stdscr.cmdwin.addstr(self.msg, look.colors['MSGPUT'])
        elif self.type == "error":
            self.core.stdscr.cmdwin.addstr(self.msg, look.colors['MSGERR'])

        (l, c) = self.core.stdscr.cmdwin.getmaxyx()
        self.core.stdscr.cmdwin.move(l-1, c-1)
        self.core.stdscr.cmdwin.noutrefresh()

class Confirm(object):
    keymap = {}

    def __init__(self, msg, options, msglist=None):
        self.msg = msg
        self.options = options
        self.cursor = 0
        self.result = None
        self.box = None
        if isinstance(msglist, list):
            self.box = ui.InfoBox(self.msg)
            self.box.show(msglist, -1)
        self.active = True
        Confirm.keymap = {
            (0, KEY_CTRL_F): lambda: self.mvcursor(1),
            (0, KEY_RIGHT ): lambda: self.mvcursor(1),
            (0, KEY_CTRL_B): lambda: self.mvcursor(-1),
            (0, KEY_LEFT  ): lambda: self.mvcursor(-1),
            (0, KEY_CTRL_G): lambda: self.hide(),
            (0, KEY_CTRL_C): lambda: self.hide(),
            (0, KEY_ESCAPE): lambda: self.hide(),
            (0, KEY_RETURN): lambda: self.get_cursor_item(),
            }
        self.core = Pyful()

    def setcursor(self, x):
        self.cursor = x

    def mvcursor(self, x):
        self.cursor += x

    def get_cursor_item(self):
        self.hide()
        self.result = self.options[self.cursor]

    def hide(self):
        self.active = False
        if self.box:
            self.box.hide()
        self.core.view()

    def view(self):
        if self.box:
            self.box.view()

        self.core.stdscr.cmdwin.erase()
        self.core.stdscr.cmdwin.move(0, 1)

        size = len(self.options)
        self.core.stdscr.cmdwin.addstr(self.msg+" ", look.colors['MSGCONFIRM'])
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor > size - 1:
            self.cursor = size - 1
        for i, s in enumerate(self.options):
            if self.cursor == i:
                try:
                    self.core.stdscr.cmdwin.addstr(s, curses.A_REVERSE)
                    self.core.stdscr.cmdwin.addstr(" ", 0)
                except Exception:
                    pass
            else:
                try:
                    self.core.stdscr.cmdwin.addstr(s+" ", 0)
                except Exception:
                    pass
        maxxy = self.core.stdscr.cmdwin.getmaxyx()
        self.core.stdscr.cmdwin.move(maxxy[0]-1, maxxy[1]-1)
        self.core.stdscr.cmdwin.noutrefresh()
        curses.doupdate()

    def input(self, meta, key):
        if self.box:
            self.box.input(meta, key)
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
