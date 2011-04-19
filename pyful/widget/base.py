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

class StandardScreen(object):
    stdscr = None
    borders = []

    @classmethod
    def destroy(cls):
        if cls.stdscr:
            curses.echo()
            curses.nocbreak()
            curses.noraw()
            curses.endwin()

    def __init__(self):
        if not self.stdscr:
            self.__class__.stdscr = curses.initscr()
            self.stdscr.notimeout(0)
            self.stdscr.keypad(1)
            curses.noecho()
            curses.cbreak()
            curses.raw()
            curses.nonl()
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
            self.stdscr.refresh()

class Screen(StandardScreen):
    def __init__(self, y, x, begy, begx, attr=0):
        self.y = y
        self.x = x
        self.begy = begy
        self.begx = begx
        self.attr = attr
        self.win = None
        self.leaveok = True

    def create_window(self):
        if not self.win:
            self.win = curses.newwin(self.y, self.x, self.begy, self.begx)
            self.win.bkgd(self.attr)
            self.win.leaveok(self.leaveok)

    def unlink_window(self):
        if self.win:
            self.win.erase()
            self.win = None

    def resize(self, y, x, begy, begx):
        self.win = None
        self.y = y
        self.x = x
        self.begy = begy
        self.begx = begx

class Panel(Screen):
    def __init__(self):
        Screen.__init__(self, 1, 1, 0, 0, 0)
        self.active = False

    def show(self):
        self.active = True

    def hide(self):
        self.unlink_window()
        self.active = False

    def hidden(self):
        return not self.active

class WidgetAlreadyRegistered(Exception):
    pass

class Widget(StandardScreen):
    widgets = {}

    @classmethod
    def refresh_all_widgets(cls):
        curses.endwin()
        cls.stdscr.refresh()
        for widget in cls.widgets.values():
            widget.refresh()

    def __init__(self, name=None):
        self.panel = Panel()
        if name:
            if not name in self.widgets:
                self.widgets[name] = self
            else:
                raise WidgetAlreadyRegistered("`{0}' already registered.".format(name))

    @property
    def active(self):
        return self.panel.active

    def refresh(self):
        pass
