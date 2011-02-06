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

class StandardScreen(object):
    stdscr = None
    cmdwin = None

    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)
        self.stdscr.notimeout(0)
        curses.noecho()
        curses.cbreak()
        curses.raw()
        curses.start_color()
        curses.use_default_colors()

        self.maxy, self.maxx = self.stdscr.getmaxyx()
        self.cmdwin = curses.newwin(2, self.maxx, self.maxy-2, 0)

    def getch(self):
        meta = False
        while True:
            key = self.stdscr.getch()
            if meta:
                if key == 27:
                    return (False, key)
                return (True, key)
            if key == 27:
                meta = True
            else:
                return (False, key)

    def refresh(self):
        self.stdscr.refresh()

    def resize(self):
        self.maxy, self.maxx = self.stdscr.getmaxyx()

    def resize_cmdwin(self):
        self.cmdwin = curses.newwin(2, self.maxx, self.maxy-2, 0)

    def destroy(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_singleton_instances'):
            cls._singleton_instances = {}
            instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._singleton_instances[hash(cls)] = instance
            instance.init_singleton_instance(*args, **kwargs)
        return cls._singleton_instances[hash(cls)]

    def init_singleton_instance(self):
        raise(Exception, "Singleton class must override this method.")

class Pyful(Singleton):
    """PYthon File management UtiLity"""

    started = None
    stdscr = None
    binpath = None
    environs = {
        'EDITOR': 'vim',
        'PAGER': 'less',
        'TRASHBOX': '~/.pyful/trashbox',
        'RCFILE': '~/.pyful/rc.py',
        'PLATFORM': sys.platform
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
            self.stdscr = StandardScreen()

            self.filer.titlebar = curses.newwin(1, self.stdscr.maxx, 0, 0)
            self.filer.default_init()

            self.message.init_messagebox()

            from pyful import ui
            ui.init_ui()

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
            (meta, key) = self.stdscr.getch()
            if key != -1:
                self.input(meta, key)
                self.view()

    def main_loop_nodelay(self):
        self.stdscr.stdscr.timeout(10)
        (meta, key) = self.stdscr.getch()
        if key != -1:
            self.input(meta, key)
            self.view()
        self.stdscr.stdscr.timeout(-1)

    def refresh(self):
        curses.endwin()
        self.stdscr.refresh()
        self.stdscr.resize()
        self.stdscr.resize_cmdwin()
        self.filer.workspace.resize()
        from pyful import ui
        ui.InfoBox.resize()
        self.message.messagebox.resize()

    def setsignal(self):
        def _signal(signalnum, stackframe):
            self.refresh()
        signal.signal(signal.SIGWINCH, _signal)

    def resetsignal(self):
        signal.signal(signal.SIGWINCH, signal.SIG_IGN)

    def load_rcfile(self, path=None):
        if path is None:
            path = os.path.expanduser(self.environs['RCFILE'])
            if not os.path.exists(path):
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc.py')
        with open(path, 'r') as rc:
            exec(rc.read(), locals())
        self.environs['RCFILE'] = path

    def check_rcfile_version(self, version):
        pass

    def create_config(self):
        confdir = os.path.expanduser('~/.pyful')
        if not os.path.exists(confdir):
            os.makedirs(confdir, 0o700)

        rcfile = os.path.join(confdir, 'rc.py')
        if not os.path.exists(rcfile):
            default = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc.py')
            shutil.copy(default, rcfile)

