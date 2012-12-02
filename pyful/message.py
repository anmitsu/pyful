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
import threading

from pyful import look
from pyful import util
from pyful import widget
from pyful import widgets

from pyful.widget.base import Widget
from pyful.widget.dialog import DialogBar
from pyful.widget.listbox import ListBox, Entry

def puts(string, timex=3):
    widgets.message.puts(string, timex)

def error(string, timex=3):
    widgets.message.error(string, timex)

def exception(except_cls):
    widgets.message.exception(except_cls)

def confirm(message, options, entries=None, position=0):
    return widgets.message.confirm(message, options, entries, position)

def forcedraw():
    widgets.message.draw()
    curses.doupdate()

def drawhistroy():
    widgets.message.draw_histroy()

class Message(Widget):
    maxsave = 100
    rlock = threading.RLock()

    def __init__(self):
        Widget.__init__(self, "Message")
        self.messages = []
        self.timer = None
        self.messagebox = MessageBox()
        self.confirmbox = ConfirmBox()

    def refresh(self):
        self.messagebox.refresh()
        self.confirmbox.refresh()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(timex, self.hide)
        self.timer.setDaemon(True)
        self.timer.start()

    def addtext(self, text, attr=0, timex=3):
        for t in text.splitlines():
            if not t:
                continue
            try:
                if isinstance(t, bytes):
                    t = t.decode().expandtabs()
                else:
                    t = util.U(t).expandtabs()
            except UnicodeError:
                t = "????? - Invalid encoding"
            self.messages.insert(0, Entry(t, attr=attr))
        self.messages = self.messages[:self.maxsave]
        if timex:
            self.start_timer(timex)

    def puts(self, text, timex=3):
        self.panel.show()
        self.addtext(text, look.colors["PutsMessage"], timex)

    def error(self, text, timex=3):
        self.panel.show()
        self.addtext(text, look.colors["ErrorMessage"], timex)

    def exception(self, except_cls):
        self.error("{0}: {1}".format(except_cls.__class__.__name__, except_cls))

    def confirm(self, message, options, entries=None, position=0):
        util.global_synchro_event.wait()
        util.global_synchro_event.clear()
        self.confirmbox.setcursor(position)
        ret = self.confirmbox.run(message, options, entries)
        util.global_synchro_event.set()
        return ret

    def draw_histroy(self):
        self.confirm("Message history", ["Close"], self.messages)

    def hide(self):
        with self.rlock:
            self.panel.hide()
            self.messagebox.hide()

    def draw(self):
        with self.rlock:
            self.messagebox.show(self.messages)
            self.messagebox.draw()

class MessageBox(ListBox):
    height = 4

    def __init__(self):
        ListBox.__init__(self)
        self.lb = -1

    def refresh(self):
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(self.height+2, x, y-self.height-4, 0)
        self.panel.attr = look.colors["MessageWindow"]

class ConfirmBox(DialogBar):
    def __init__(self):
        DialogBar.__init__(self)

    def run(self, message, options, entries=None):
        self.result = None
        self.show(message, options, entries)
        def _draw():
            widgets.filer.draw()
            self.draw()
        ui = widget.ui.UI(_draw, self.input)
        while self.active:
            ui.run()
        return self.result





