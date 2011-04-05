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

def puts(string, timex=3):
    ui.getwidget("Message").puts(string, timex)

def error(string, timex=3):
    ui.getwidget("Message").error(string, timex)

def exception(except_cls):
    ui.getwidget("Message").exception(except_cls)

def confirm(message, options, info=None, position=0):
    return ui.getwidget("Message").confirm(message, options, info, position)

def viewhistroy():
    ui.getwidget("Message").view_histroy()

class Message(ui.Widget):
    history = 100

    def __init__(self):
        ui.Widget.__init__(self, "Message")
        self.msg = []
        self.timer = None
        self.messagebox = MessageBox()
        self.confirmbox = ConfirmBox()

    def start_timer(self, timex):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(timex, self.hide)
        self.timer.setDaemon(True)
        self.timer.start()

    def puts(self, string, timex=3):
        self.active = True
        string = string.expandtabs()
        string = re.sub(r"[\n\r]", "", string)
        self.msg.insert(0, ui.InfoBoxContext(string, attr=look.colors["PutsMessage"]))
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def error(self, string, timex=3):
        self.active = True
        string = string.expandtabs()
        string = re.sub(r"[\n\r]", "", string)
        self.msg.insert(0, ui.InfoBoxContext(string, attr=look.colors["ErrorMessage"]))
        if self.history < len(self.msg):
            self.msg.pop()
        self.view()
        if timex:
            self.start_timer(timex)

    def exception(self, except_cls):
        self.error("{0}: {1}".format(except_cls.__class__.__name__, except_cls))

    def confirm(self, message, options, info=None, position=0):
        self.confirmbox.setconfirmcursor(position)
        return self.confirmbox.run(message, options, info)

    def view_histroy(self):
        self.confirm("Message history", ["Close"], self.msg)

    def hide(self):
        self.active = False
        self.messagebox.hide()

    def view(self):
        if ui.getwidget("Cmdline").is_active or ui.getwidget("Filer").finder.active:
            return
        self.messagebox.show(self.msg)
        self.messagebox.view()

class MessageBox(ui.InfoBox):
    height = 4

    def __init__(self):
        ui.InfoBox.__init__(self, "MessageBox")
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

class ConfirmBox(ui.InfoBox):
    def __init__(self):
        ui.InfoBox.__init__(self, "ConfirmBox")
        self.lb = -1
        self.options = []
        self.message = ""
        self.result = None
        self.confirmcursor = 0
        self.keymap.update({
            "C-f"    : lambda: self.mvconfirmcursor(1),
            "<right>": lambda: self.mvconfirmcursor(1),
            "C-b"    : lambda: self.mvconfirmcursor(-1),
            "<left>" : lambda: self.mvconfirmcursor(-1),
            "C-g"    : lambda: self.cancel(),
            "C-c"    : lambda: self.cancel(),
            "ESC"    : lambda: self.cancel(),
            "RET"    : lambda: self.get_confirm_option(),
            })

    def run(self, message, options, info=None):
        self.message = message
        self.options = options
        if info:
            myinfo = []
            for item in info:
                if isinstance(item, ui.InfoBoxContext):
                    myinfo.append(item)
                else:
                    myinfo.append(ui.InfoBoxContext(item))
            self.show(myinfo)
        viewer = ui.Viewer(self.view)
        controller = ui.Controller(self.input)
        while self.options:
            viewer.view_and_update()
            controller.control()
        result = self.result
        self.result = None
        return result

    def setconfirmcursor(self, x):
        self.confirmcursor = x

    def mvconfirmcursor(self, x):
        self.confirmcursor += x

    def get_confirm_option(self):
        self.result = self.options[self.confirmcursor]
        self.message = ""
        self.options = []
        self.confirmcursor = 0
        self.hide()

    def cancel(self):
        self.message = ""
        self.options = []
        self.confirmcursor = 0
        self.hide()

    def view(self):
        super(self.__class__, self).view()

        cmdscr = ui.getwidget("Cmdscr").win
        cmdscr.erase()
        y, x = cmdscr.getmaxyx()
        size = len(self.options)

        try:
            cmdscr.addstr(0, 1, self.message+" ",
                          look.colors["ConfirmMessage"])
        except curses.error:
            cmdscr.erase()
            maxwidth = x-2-util.termwidth(" ".join(self.options))
            cmdscr.addstr(0, 1, util.mbs_ljust(self.message+" ", maxwidth),
                          look.colors["ConfirmMessage"])

        if self.confirmcursor < 0:
            self.confirmcursor = 0
        elif self.confirmcursor > size - 1:
            self.confirmcursor = size - 1
        for i, s in enumerate(self.options):
            if self.confirmcursor == i:
                try:
                    cmdscr.addstr(s, curses.A_REVERSE)
                    cmdscr.addstr(" ", 0)
                except curses.error:
                    pass
            else:
                try:
                    cmdscr.addstr(s+" ", 0)
                except curses.error:
                    pass
        cmdscr.move(y-1, x-1)
        cmdscr.noutrefresh()
