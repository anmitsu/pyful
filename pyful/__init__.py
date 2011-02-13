# initializer and core of Pyful
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

"""Python file management utility.
This application is CUI filer of the keyboard operation for Linux."""

__version__ = "0.2.2"

import curses
import os
import signal
import sys

from pyful import look
from pyful import ui

def loadrcfile(path=None, started=True):
    if path is None:
        defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc.py')
        path = os.path.expanduser(Pyful.environs['RCFILE'])
        if not os.path.exists(path):
            path = defpath
    try:
        with open(path, 'r') as rc:
            exec(rc.read(), locals())
        Pyful.environs['RCFILE'] = path
    except Exception as e:
        if started:
            with open(defpath, 'r') as rc:
                exec(rc.read(), locals())
            Pyful.environs['RCFILE'] = defpath
        return e

def setsignal():
    def _signal(signalnum, stackframe):
        ui.refresh()
    signal.signal(signal.SIGWINCH, _signal)

def resetsignal():
    signal.signal(signal.SIGWINCH, signal.SIG_DFL)

def atinit(func, *args, **kwargs):
    Pyful.initfuncs.append(lambda: func(*args, **kwargs))

def atexit(func, *args, **kwargs):
    Pyful.exitfuncs.append(lambda: func(*args, **kwargs))

class Pyful(object):
    """PYthon File management UtiLity"""

    environs = {
        'EDITOR': 'vim',
        'PAGER': 'less',
        'TRASHBOX': '~/.pyful/trashbox',
        'RCFILE': '~/.pyful/rc.py',
        'LOOKS': look.looks['default'],
        'PLATFORM': sys.platform,
        }
    binpath = None
    initfuncs = []
    exitfuncs = []

    def __init__(self):
        from pyful.cmdline import Cmdline
        from pyful.filer import Filer
        from pyful.message import Message
        from pyful.menu import Menu

        self.cmdline = Cmdline()
        self.filer = Filer()
        self.message = Message()
        self.menu = Menu()

        from pyful.process import view_process
        self.view_process = view_process

    def init_function(self):
        for func in self.initfuncs: func()

    def exit_function(self):
        for func in self.exitfuncs: func()

    def view(self):
        self.filer.view()
        if self.menu.is_active:
            self.menu.view()
        if self.cmdline.is_active:
            self.cmdline.view()
        elif self.message.is_active:
            self.message.view()
        self.view_process()
        curses.doupdate()

    def input(self, meta, key):
        if self.cmdline.is_active:
            self.cmdline.input(meta, key)
        elif self.menu.is_active:
            self.menu.input(meta, key)
        else:
            self.filer.input(meta, key)

    def main_loop(self):
        while True:
            self.view()
            (meta, key) = ui.getch()
            if key != -1:
                self.input(meta, key)
