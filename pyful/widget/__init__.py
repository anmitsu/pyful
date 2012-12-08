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

__all__ = ["base", "dialog", "gauge", "listbox", "textbox", "ui"]

import curses

from pyful.widget import *

def define_key(obj, keymap, override=False):
    if obj.__class__.keymap is None:
        obj.__class__.keymap = keymap
    else:
        if override:
            obj.__class__.keymap = keymap
        else:
            obj.__class__.keymap.update(keymap)

def get(name):
    return base.Widget.widgets[name]

def refresh_all_widgets():
    base.Widget.refresh_all_widgets()

def start_curses():
    try:
        curses.noecho()
        curses.cbreak()
        curses.raw()
    except curses.error:
        base.StandardScreen()

def end_curses():
    base.StandardScreen.destroy()
