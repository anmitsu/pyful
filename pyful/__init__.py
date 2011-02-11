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

import os
import sys
import curses
import signal
import shutil

from pyful import ui

def loadrcfile(path=None):
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
        with open(defpath, 'r') as rc:
            exec(rc.read(), locals())
        Pyful.environs['RCFILE'] = defpath
        return e

def createconfig():
    confdir = os.path.expanduser('~/.pyful')
    if not os.path.exists(confdir):
        os.makedirs(confdir, 0o700)

    rcfile = os.path.join(confdir, 'rc.py')
    if not os.path.exists(rcfile):
        default = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc.py')
        shutil.copy(default, rcfile)

def refresh():
    curses.endwin()
    ui.getstdscr().refresh()
    ui.resize()
    from pyful.filer import Filer
    Filer().workspace.resize()
    from pyful.message import Message
    Message.instance.messagebox.resize()

def setsignal():
    def _signal(signalnum, stackframe):
        refresh()
    signal.signal(signal.SIGWINCH, _signal)

def resetsignal():
    signal.signal(signal.SIGWINCH, signal.SIG_DFL)

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_singleton_instances'):
            cls._singleton_instances = {}
            instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._singleton_instances[hash(cls)] = instance
            instance.init_singleton_instance(*args, **kwargs)
        return cls._singleton_instances[hash(cls)]

    def init_singleton_instance(self):
        raise Exception("Singleton class must override this method.")

class Pyful(Singleton):
    """PYthon File management UtiLity"""

    started = None
    binpath = None
    environs = {
        'EDITOR': 'vim',
        'PAGER': 'less',
        'TRASHBOX': '~/.pyful/trashbox',
        'RCFILE': '~/.pyful/rc.py',
        'PLATFORM': sys.platform,
        }
    __initfuncs = []
    __exitfuncs = []

    def init_singleton_instance(self):
        from pyful.message import Message
        self.message = Message()

        from pyful.cmdline import Cmdline
        self.cmdline = Cmdline()

        from pyful.filer import Filer
        self.filer = Filer()

        from pyful.menu import Menu
        self.menu = Menu()

        from pyful.process import view_process
        self.view_process = view_process

    def start_curses(self):
        if not self.started:
            ui.init_ui()

            self.filer.default_init()

            self.message.init_messagebox()

            from pyful import look
            look.init_colors()

    def atinit(self, func, *args, **kwargs):
        self.__initfuncs.append(lambda: func(*args, **kwargs))

    def init_function(self):
        for func in self.__initfuncs: func()

    def atexit(self, func, *args, **kwargs):
        self.__exitfuncs.append(lambda: func(*args, **kwargs))

    def exit_function(self):
        for func in self.__exitfuncs: func()

    def view(self):
        self.filer.view()
        if self.menu.active:
            self.menu.view()
        if self.cmdline.active:
            self.cmdline.view()
        elif self.message.active:
            self.message.view()
        self.view_process()
        curses.doupdate()

    def input(self, meta, key):
        if self.cmdline.active:
            self.cmdline.input(meta, key)
        elif self.menu.active:
            self.menu.input(meta, key)
        else:
            self.filer.input(meta, key)

    def main_loop(self):
        while True:
            self.view()
            (meta, key) = ui.getch()
            if key != -1:
                self.input(meta, key)

    def main_loop_nodelay(self):
        stdscr = ui.getstdscr()
        stdscr.timeout(10)
        self.view()
        (meta, key) = ui.getch()
        if key != -1:
            self.input(meta, key)
        stdscr.timeout(-1)

    def check_rcfile_version(self, version):
        pass

