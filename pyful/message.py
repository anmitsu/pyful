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

from pyful import look
from pyful import ui
from pyful import util
from pyful.keymap import *

def puts(string, timex=3):
    ui.getcomponent("Message").puts(string, timex)

def error(string, timex=3):
    ui.getcomponent("Message").error(string, timex)

def exception(except_cls):
    ui.getcomponent("Message").exception(except_cls)

def confirm(msg, options, msglist=None, position=0):
    return ui.getcomponent("Message").confirm(msg, options, msglist, position)

def timerkill():
    t = ui.getcomponent("Message").timer
    if t: t.cancel()

def viewhistroy():
    ui.getcomponent("Message").view_histroy()

class Message(ui.Component):
    history = 100

    def __init__(self):
        ui.Component.__init__(self, "Message")
        self.msg = []
        self.timer = None
        self.messagebox = MessageBox()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(timex, self.hide)
        self.timer.start()

    def puts(self, string, timex=3):
        self.active = True
        msg = re.sub(r"[\n\r\t]", "", util.U(string))
        self.msg.insert(0, ui.InfoBoxContext(msg, attr=look.colors['PutsMessage']))
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def error(self, string, timex=3):
        self.active = True
        msg = re.sub(r"[\n\r\t]", "", util.U(string))
        self.msg.insert(0, ui.InfoBoxContext(msg, attr=look.colors['ErrorMessage']))
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def exception(self, except_cls):
        self.error('{0}: {1}'.format(except_cls.__class__.__name__, except_cls))

    def confirm(self, msg, options, msglist=None, position=0):
        cnf = Confirm(msg, options, msglist)
        cnf.setcursor(position)
        while cnf.active:
            cnf.view()
            (meta, key) = ui.getch()
            cnf.input(meta, key)
        return cnf.result

    def view_histroy(self):
        self.confirm("Message history", ["Close"], [m.string for m in self.msg], -1)

    def hide(self):
        self.active = False

    def view(self):
        if ui.getcomponent("Cmdline").is_active or ui.getcomponent("Filer").finder.active:
            return
        self.messagebox.show(self.msg, -1)
        self.messagebox.view()

class MessageBox(ui.InfoBox):
    height = 2

    def __init__(self):
        ui.InfoBox.__init__(self, "MessageBox")
        self.win = None

    def resize(self):
        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        self.win = curses.newwin(self.height+2, x, y-self.height-4, 0)
        self.win.bkgd(look.colors['MessageWindow'])

class Confirm(object):
    keymap = {}
    box = ui.InfoBox("Confirm")

    def __init__(self, msg, options, msglist=None):
        self.msg = msg
        self.options = options
        self.cursor = 0
        self.result = None
        if isinstance(msglist, list):
            self.box.show([ui.InfoBoxContext(msg) for msg in msglist], -1)
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

    def view(self):
        if self.box:
            self.box.view()

        cmdscr = ui.getcomponent("Cmdscr").win
        cmdscr.erase()
        cmdscr.move(0, 1)

        size = len(self.options)
        cmdscr.addstr(self.msg+" ", look.colors['ConfirmMessage'])
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor > size - 1:
            self.cursor = size - 1
        for i, s in enumerate(self.options):
            if self.cursor == i:
                try:
                    cmdscr.addstr(s, curses.A_REVERSE)
                    cmdscr.addstr(" ", 0)
                except Exception:
                    pass
            else:
                try:
                    cmdscr.addstr(s+" ", 0)
                except Exception:
                    pass
        (y, x) = cmdscr.getmaxyx()
        cmdscr.move(y-1, x-1)
        cmdscr.noutrefresh()
        curses.doupdate()

    def input(self, meta, key):
        if self.box:
            self.box.input(meta, key)
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()

