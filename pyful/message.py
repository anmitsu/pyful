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
import re
from threading import Timer

from pyful import Pyful, Singleton
from pyful import look
from pyful import ui
from pyful import util
from pyful.keymap import *

class Message(Singleton):
    history = 100

    def init_singleton_instance(self):
        self.msg = []
        self.active = False
        self.timer = None
        self.core = Pyful()

    def init_messagebox(self):
        self.messagebox = MessageBox()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(timex, self.hide)
        self.timer.start()

    def puts(self, string, timex=4):
        self.active = True
        msg = (re.sub(r"[\n\r\t]", "", util.unistr(string)), look.colors['MSGPUT'])
        self.msg.insert(0, msg)
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def error(self, string, timex=4):
        self.active = True
        msg = (re.sub(r"[\n\r\t]", "", util.unistr(string)), look.colors['MSGERR'])
        self.msg.insert(0, msg)
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def exception(self, except_cls):
        self.error('%s: %s' % (except_cls.__class__.__name__, str(except_cls)))

    def confirm(self, msg, options, msglist=None, position=0):
        self.core.view()
        cnf = Confirm(msg, options, msglist)
        cnf.setcursor(position)
        while cnf.active:
            cnf.view()
            (meta, key) = self.core.stdscr.getch()
            cnf.input(meta, key)
        return cnf.result

    def view_histroy(self):
        self.confirm("Message history", ["Close"], [m[0] for m in self.msg], -1)

    def hide(self):
        self.active = False

    def view(self):
        self.messagebox.view(self.msg)

class MessageBox(object):
    height = 2

    def __init__(self):
        self.core = Pyful()
        self.win = curses.newwin(self.height+2, self.core.stdscr.maxx, self.core.stdscr.maxy-self.height-4, 0)

    def resize(self):
        self.win = curses.newwin(self.height+2, self.core.stdscr.maxx, self.core.stdscr.maxy-self.height-4, 0)

    def view(self, msglist):
        if not msglist:
            return
        self.win.box()
        size = len(msglist)
        (y,x) = self.win.getmaxyx()
        self.win.move(0, 2)
        self.win.addstr("Messages(%s)" % size, curses.A_BOLD)
        (y,x) = self.win.getmaxyx()
        for i in range(0, size):
            if self.height <= i: break
            self.win.move(i+1, 2)
            msg = msglist[i]
            self.win.addstr(util.mbs_ljust(msg[0], x-4), msg[1])
        self.win.noutrefresh()

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
