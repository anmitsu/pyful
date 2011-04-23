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

looks = {
    "default": {
        "Window"                : ("default" ,  "default" ,  "normal"),
        "Titlebar"              : ("default" ,  "default" ,  "normal"),
        "TitlebarFocus"         : ("default" ,  "default" ,  "reverse"),
        "CmdlineWindow"         : ("default" ,  "default" ,  "normal"),
        "MenuWindow"            : ("default" ,  "default" ,  "normal"),
        "TextBoxWindow"         : ("default" ,  "default" ,  "normal"),
        "ListBoxWindow"         : ("default" ,  "default" ,  "normal"),
        "ListBoxTitle"          : ("default" ,  "default" ,  "bold | underline"),
        "ProgressGauge"         : ("default" ,  "blue"    ,  "normal"),
        "DirectoryPath"         : ("default" ,  "default" ,  "bold"),
        "MarkFile"              : ("yellow"  ,  "default" ,  "bold"),
        "LinkFile"              : ("magenta" ,  "default" ,  "normal"),
        "LinkDir"               : ("magenta" ,  "default" ,  "bold"),
        "Directory"             : ("cyan"    ,  "default" ,  "bold"),
        "ExecutableFile"        : ("red"     ,  "default" ,  "bold"),
        "MessageWindow"         : ("default" ,  "default" ,  "normal"),
        "PutsMessage"           : ("default" ,  "default" ,  "normal"),
        "ErrorMessage"          : ("red"     ,  "default" ,  "bold"),
        "DialogMessage"         : ("cyan"    ,  "default" ,  "bold"),
        "FinderWindow"          : ("black"   ,  "cyan"    ,  "normal"),
        "FinderPrompt"          : ("cyan"    ,  "default" ,  "bold"),
        "WorkspaceFocus"        : ("black"   ,  "cyan"    ,  "normal"),
        "CmdlineOptions"        : ("yellow"  ,  "default" ,  "normal"),
        "CmdlineSeparator"      : ("blue"    ,  "default" ,  "normal"),
        "CmdlinePythonFunction" : ("cyan"    ,  "default" ,  "bold"),
        "CmdlineMacro"          : ("magenta" ,  "default" ,  "normal"),
        "CmdlineProgram"        : ("green"   ,  "default" ,  "bold"),
        "CmdlineNoProgram"      : ("red"     ,  "default" ,  "normal"),
        "CmdlinePrompt"         : ("cyan"    ,  "default" ,  "bold"),
        "CandidateHighlight"    : ("default" ,  "default" ,  "bold"),
        },

    "midnight": {
        "Window"                : ("white"   ,  "blue"    ,  "normal"),
        "Titlebar"              : ("white"   ,  "blue"    ,  "normal"),
        "TitlebarFocus"         : ("black"   ,  "cyan"    ,  "normal"),
        "MenuWindow"            : ("white"   ,  "blue"    ,  "normal"),
        "TextBoxWindow"         : ("white"   ,  "blue"    ,  "normal"),
        "ListBoxWindow"         : ("white"   ,  "blue"    ,  "normal"),
        "ListBoxTitle"          : ("black"   ,  "white"   ,  "normal"),
        "ProgressGauge"         : ("white"   ,  "cyan"    ,  "normal"),
        "DirectoryPath"         : ("black"   ,  "white"   ,  "normal"),
        "MarkFile"              : ("yellow"  ,  "blue"    ,  "bold"),
        "LinkFile"              : ("white"   ,  "blue"    ,  "normal"),
        "LinkDir"               : ("white"   ,  "blue"    ,  "bold"),
        "Directory"             : ("white"   ,  "blue"    ,  "bold"),
        "ExecutableFile"        : ("green"   ,  "blue"    ,  "bold"),
        "MessageWindow"         : ("white"   ,  "blue"    ,  "normal"),
        "PutsMessage"           : ("white"   ,  "blue"    ,  "normal"),
        "ErrorMessage"          : ("red"     ,  "blue"    ,  "normal"),
        "DialogMessage"         : ("white"   ,  "blue"    ,  "bold"),
        "FinderWindow"          : ("black"   ,  "cyan"    ,  "normal"),
        "FinderPrompt"          : ("white"   ,  "blue"    ,  "bold"),
        "WorkspaceFocus"        : ("black"   ,  "cyan"    ,  "normal"),
        "CmdlineWindow"         : ("default" ,  "default" ,  "normal"),
        "CmdlineOptions"        : ("yellow"  ,  "default" ,  "normal"),
        "CmdlineSeparator"      : ("blue"    ,  "default" ,  "normal"),
        "CmdlinePythonFunction" : ("cyan"    ,  "default" ,  "bold"),
        "CmdlineMacro"          : ("magenta" ,  "default" ,  "normal"),
        "CmdlineProgram"        : ("green"   ,  "default" ,  "bold"),
        "CmdlineNoProgram"      : ("red"     ,  "default" ,  "normal"),
        "CmdlinePrompt"         : ("cyan"    ,  "default" ,  "bold"),
        "CandidateHighlight"    : ("white"   ,  "blue"    ,  "bold"),
        },

    "dark": {
        "Window"                : ("white"   ,  "black" ,  "normal"),
        "Titlebar"              : ("white"   ,  "black" ,  "normal"),
        "TitlebarFocus"         : ("white"   ,  "black" ,  "reverse"),
        "MenuWindow"            : ("white"   ,  "black" ,  "normal"),
        "TextBoxWindow"         : ("white"   ,  "black" ,  "normal"),
        "ListBoxWindow"         : ("white"   ,  "black" ,  "normal"),
        "ListBoxTitle"          : ("white"   ,  "black" ,  "bold | underline"),
        "ProgressGauge"         : ("white"   ,  "blue"  ,  "normal"),
        "DirectoryPath"         : ("white"   ,  "black" ,  "bold"),
        "MarkFile"              : ("yellow"  ,  "black" ,  "bold"),
        "LinkFile"              : ("magenta" ,  "black" ,  "normal"),
        "LinkDir"               : ("magenta" ,  "black" ,  "bold"),
        "Directory"             : ("cyan"    ,  "black" ,  "bold"),
        "ExecutableFile"        : ("red"     ,  "black" ,  "bold"),
        "MessageWindow"         : ("white"   ,  "black" ,  "normal"),
        "PutsMessage"           : ("white"   ,  "black" ,  "normal"),
        "ErrorMessage"          : ("red"     ,  "black" ,  "normal"),
        "DialogMessage"         : ("cyan"    ,  "black" ,  "bold"),
        "FinderWindow"          : ("black"   ,  "cyan"  ,  "normal"),
        "FinderPrompt"          : ("cyan"    ,  "black" ,  "bold"),
        "WorkspaceFocus"        : ("black"   ,  "cyan"  ,  "normal"),
        "CmdlineWindow"         : ("white"   ,  "black" ,  "normal"),
        "CmdlineOptions"        : ("yellow"  ,  "black" ,  "normal"),
        "CmdlineSeparator"      : ("blue"    ,  "black" ,  "normal"),
        "CmdlinePythonFunction" : ("cyan"    ,  "black" ,  "bold"),
        "CmdlineMacro"          : ("magenta" ,  "black" ,  "normal"),
        "CmdlineProgram"        : ("green"   ,  "black" ,  "bold"),
        "CmdlineNoProgram"      : ("red"     ,  "black" ,  "normal"),
        "CmdlinePrompt"         : ("cyan"    ,  "black" ,  "bold"),
        "CandidateHighlight"    : ("cyan"    ,  "black" ,  "bold"),
        },

    "light": {
        "Window"                : ("black"   ,  "white"  ,  "normal"),
        "Titlebar"              : ("black"   ,  "white"  ,  "normal"),
        "TitlebarFocus"         : ("black"   ,  "cyan"   ,  "normal"),
        "MenuWindow"            : ("black"   ,  "white"  ,  "normal"),
        "TextBoxWindow"         : ("black"   ,  "white"  ,  "normal"),
        "ListBoxWindow"         : ("black"   ,  "white"  ,  "normal"),
        "ListBoxTitle"          : ("black"   ,  "cyan"   ,  "underline"),
        "ProgressGauge"         : ("black"   ,  "cyan"   ,  "normal"),
        "DirectoryPath"         : ("blue"    ,  "white"  ,  "bold"),
        "MarkFile"              : ("black"   ,  "yellow" ,  "normal"),
        "LinkFile"              : ("magenta" ,  "white"  ,  "normal"),
        "LinkDir"               : ("magenta" ,  "white"  ,  "bold"),
        "Directory"             : ("blue"    ,  "white"  ,  "bold"),
        "ExecutableFile"        : ("red"     ,  "white"  ,  "bold"),
        "MessageWindow"         : ("black"   ,  "white"  ,  "normal"),
        "PutsMessage"           : ("black"   ,  "white"  ,  "normal"),
        "ErrorMessage"          : ("red"     ,  "white"  ,  "normal"),
        "DialogMessage"         : ("blue"    ,  "white"  ,  "bold"),
        "FinderWindow"          : ("black"   ,  "cyan"   ,  "normal"),
        "FinderPrompt"          : ("blue"    ,  "white"  ,  "bold"),
        "WorkspaceFocus"        : ("black"   ,  "cyan"   ,  "normal"),
        "CmdlineWindow"         : ("black"   ,  "white"  ,  "normal"),
        "CmdlineOptions"        : ("black"   ,  "yellow" ,  "normal"),
        "CmdlineSeparator"      : ("blue"    ,  "white"  ,  "normal"),
        "CmdlinePythonFunction" : ("black"   ,  "green"  ,  "normal"),
        "CmdlineMacro"          : ("magenta" ,  "white"  ,  "normal"),
        "CmdlineProgram"        : ("black"   ,  "green"  ,  "normal"),
        "CmdlineNoProgram"      : ("red"     ,  "white"  ,  "normal"),
        "CmdlinePrompt"         : ("blue"    ,  "white"  ,  "bold"),
        "CandidateHighlight"    : ("blue"    ,  "white"  ,  "bold"),
        },
    }

class Look(object):
    pass

Look.mylook = "default"

def _init_color_table():
    for name in looks["default"].keys():
        colors[name] = 0
_init_color_table()

def init_colors():
    mylook = looks.get(Look.mylook, looks["default"])
    cols = {}
    attrs = {}
    for m in dir(curses):
        if m.startswith("COLOR_"):
            cols[m[6:].lower()] = getattr(curses, m)
        elif m.startswith("A_"):
            attrs[m[2:].lower()] = getattr(curses, m)

    if curses.has_colors():
        for i, (name, v) in enumerate(mylook.items()):
            fg, bg, attr = v
            myfg = cols.get(fg, -1)
            mybg = cols.get(bg, -1)
            myattr = 0
            for a in attr.split("|"):
                myattr |= attrs.get(a.strip(), 0)
            curses.init_pair(i+1, myfg, mybg)
            colors[name] = curses.color_pair(i+1) | myattr
    else:
        for (name, v) in mylook.items():
            fg, bg, attr = v
            myattr = 0
            for a in attr.split("|"):
                myattr |= attrs.get(a.strip(), 0)
            colors[name] = myattr
