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
import threading

from pyful import look
from pyful import ui
from pyful import widget

def puts(string, timex=3):
    widget.get("Message").puts(string, timex)

def error(string, timex=3):
    widget.get("Message").error(string, timex)

def exception(except_cls):
    widget.get("Message").exception(except_cls)

def confirm(message, options, info=None, position=0):
    return widget.get("Message").confirm(message, options, info, position)

def forcedraw():
    widget.get("Message").draw()
    curses.doupdate()

def drawhistroy():
    widget.get("Message").draw_histroy()

class Message(widget.base.Widget):
    maxsave = 100
    rlock = threading.RLock()

    def __init__(self):
        widget.base.Widget.__init__(self, "Message")
        self.messages = []
        self.timer = None
        self.messagebox = MessageBox()
        self.confirmbox = ConfirmBox()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(timex, self.hide)
        self.timer.setDaemon(True)
        self.timer.start()

    def puts(self, string, timex=3):
        self.active = True
        string = re.sub(r"[\n\r]", "", string).expandtabs()
        self.messages.insert(0, widget.infobox.Context(string, attr=look.colors["PutsMessage"]))
        if self.maxsave < len(self.messages):
            self.messages.pop()
        if timex:
            self.start_timer(timex)

    def error(self, string, timex=3):
        self.active = True
        string = re.sub(r"[\n\r]", "", string).expandtabs()
        self.messages.insert(0, widget.infobox.Context(string, attr=look.colors["ErrorMessage"]))
        if self.maxsave < len(self.messages):
            self.messages.pop()
        if timex:
            self.start_timer(timex)

    def exception(self, except_cls):
        self.error("{0}: {1}".format(except_cls.__class__.__name__, except_cls))

    def confirm(self, message, options, info=None, position=0):
        with self.confirmbox.rlock:
            self.confirmbox.setcursor(position)
            return self.confirmbox.run(message, options, info)

    def draw_histroy(self):
        self.confirm("Message history", ["Close"], self.messages)

    def hide(self):
        with self.rlock:
            self.active = False
            self.messagebox.hide()

    def draw(self):
        with self.rlock:
            self.messagebox.show(self.messages)
            self.messagebox.draw()

class MessageBox(widget.infobox.InfoBox):
    height = 4

    def __init__(self):
        widget.infobox.InfoBox.__init__(self, "MessageBox")
        self.lb = -1
        self.resize()

    def resize(self):
        self.win = None
        y, x = self.stdscr.getmaxyx()
        self.y = self.height+2
        self.x = x
        self.begy = y-self.height-4
        self.begx = 0
        self.winattr = look.colors["MessageWindow"]

class ConfirmBox(widget.dialog.DialogBox):
    rlock = threading.RLock()

    def __init__(self):
        widget.dialog.DialogBox.__init__(self, "ConfirmBox")
        self.infobox = widget.infobox.InfoBox("ConfirmInfoBox")
        self.infobox.lb = -1
        self.keymap["RET"] = self.get_result
        self.result = None

    def resize(self):
        self.win = None
        y, x = self.stdscr.getmaxyx()
        self.y = 2
        self.x = x
        self.begy = y - 2
        self.begx = 0
        self.winattr = look.colors["Window"]
        self.messageattr = look.colors["ConfirmMessage"]

    def get_result(self):
        self.result = self.cursor_item()
        self.hide()
        self.infobox.hide()

    def draw(self):
        self.infobox.draw()
        super(self.__class__, self).draw()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        elif self.infobox.active and key in self.infobox.keymap:
            self.infobox.keymap[key]()

    def run(self, message, options, info=None):
        self.result = None
        self.show(message, options)
        if info:
            _info = []
            for item in info:
                if isinstance(item, widget.infobox.Context):
                    _info.append(item)
                else:
                    _info.append(widget.infobox.Context(item))
            self.infobox.show(_info)
        drawer = ui.Drawer(self.draw)
        controller = ui.Controller(self.input)
        while self.active:
            drawer.draw_and_update()
            controller.control()
        return self.result
