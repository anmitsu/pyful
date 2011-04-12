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

    @classmethod
    def destroy(cls):
        if cls.stdscr:
            curses.echo()
            curses.nocbreak()
            curses.noraw()
            curses.endwin()

class WidgetAlreadyRegistered(Exception):
    pass

class Widget(StandardScreen):
    widgets = {}

    def __init__(self, name, register=True):
        self.active = False
        if register:
            if not name in self.widgets:
                self.widgets[name] = self
            else:
                raise WidgetAlreadyRegistered("`{0}' already registered.".format(name))
        else:
            self.widgets[name] = self.__class__

    @property
    def is_active(self):
        return self.active

    def resize(self):
        pass
