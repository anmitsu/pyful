# look.py - a look management
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

colors = {}

default = {
    "Window": (-1, -1, 0),
    "Titlebar": (-1, -1, 0),
    "TitlebarFocus": (-1, -1, curses.A_REVERSE),
    "CmdlineWindow": (-1, -1, 0),
    "InfoBoxWindow": (-1, -1, 0),
    "MarkFile": (curses.COLOR_YELLOW, -1, curses.A_BOLD),
    "LinkFile": (curses.COLOR_MAGENTA, -1, 0),
    "LinkDir": (curses.COLOR_MAGENTA, -1, curses.A_BOLD),
    "Directory": (curses.COLOR_CYAN, -1, curses.A_BOLD),
    "ExecutableFile": (curses.COLOR_RED, -1, curses.A_BOLD),
    "MessageWindow": (-1, -1, 0),
    "PutsMessage": (-1, -1, 0),
    "ErrorMessage": (curses.COLOR_RED, -1, curses.A_BOLD),
    "ConfirmMessage": (curses.COLOR_CYAN, -1, curses.A_BOLD),
    "Finder": (curses.COLOR_BLACK, curses.COLOR_CYAN, 0),
    "Workspace": (-1, -1, 0),
    "WorkspaceFocus": (curses.COLOR_BLACK, curses.COLOR_CYAN, 0),
    "CmdlineOptions": (curses.COLOR_YELLOW, -1, 0),
    "CmdlineSeparator": (curses.COLOR_BLUE, -1, 0),
    "CmdlinePythonFunction": (curses.COLOR_CYAN, -1, curses.A_BOLD),
    "CmdlineMacro": (curses.COLOR_MAGENTA, -1, 0),
    "CmdlineProgram": (curses.COLOR_GREEN, -1, curses.A_BOLD),
    "CmdlineNoProgram": (curses.COLOR_RED, -1, 0),
    "CmdlinePrompt": (curses.COLOR_CYAN, -1, curses.A_BOLD),
    "CandidateHilight": (-1, -1, curses.A_BOLD)
}

midnight = {
    "Window": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "Titlebar": (curses.COLOR_BLACK, curses.COLOR_CYAN, 0),
    "TitlebarFocus": (curses.COLOR_WHITE, curses.COLOR_BLACK, curses.A_BOLD),
    "InfoBoxWindow": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "MarkFile": (curses.COLOR_YELLOW, curses.COLOR_BLUE, curses.A_BOLD),
    "LinkFile": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "LinkDir": (curses.COLOR_WHITE, curses.COLOR_BLUE, curses.A_BOLD),
    "Directory": (curses.COLOR_WHITE, curses.COLOR_BLUE, curses.A_BOLD),
    "ExecutableFile": (curses.COLOR_GREEN, curses.COLOR_BLUE, curses.A_BOLD),
    "MessageWindow": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "PutsMessage": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "ErrorMessage": (curses.COLOR_RED, curses.COLOR_BLUE, 0),
    "ConfirmMessage": (curses.COLOR_WHITE, -1, curses.A_BOLD),
    "Finder": (curses.COLOR_BLACK, curses.COLOR_CYAN, 0),
    "Workspace": (curses.COLOR_WHITE, curses.COLOR_BLUE, 0),
    "WorkspaceFocus": (curses.COLOR_WHITE, curses.COLOR_BLACK, curses.A_BOLD),
    "CmdlineWindow": (-1, -1, 0),
    "CmdlineOptions": (curses.COLOR_YELLOW, -1, 0),
    "CmdlineSeparator": (curses.COLOR_BLUE, -1, 0),
    "CmdlinePythonFunction": (curses.COLOR_CYAN, -1, curses.A_BOLD),
    "CmdlineMacro": (curses.COLOR_MAGENTA, -1, 0),
    "CmdlineProgram": (curses.COLOR_GREEN, -1, curses.A_BOLD),
    "CmdlineNoProgram": (curses.COLOR_RED, -1, 0),
    "CmdlinePrompt": (curses.COLOR_WHITE, -1, curses.A_BOLD),
    "CandidateHilight": (curses.COLOR_WHITE, curses.COLOR_BLUE, curses.A_BOLD)
    }

for k in default.keys():
    colors.update({k: 0})

def init_colors():
    from pyful import Pyful
    for i, (name, v) in enumerate(Pyful.environs['LOOKS'].items()):
        curses.init_pair(i+1, v[0], v[1])
        colors.update({name: curses.color_pair(i+1) | v[2]})
