# help.py - help management
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
import os
import re

from pyful import message
from pyful import ui
from pyful import util
from pyful import keymap

class Help(ui.InfoBox):
    def __init__(self):
        ui.InfoBox.__init__(self, "Help")
        self.indent = ' ' * 4

    def parse_docstring(self, doc):
        info = []
        info.append(["Documentation:", curses.A_BOLD])
        for line in doc.split(os.linesep):
            line = line.strip()

            if line.startswith('*'):
                count = re.match(r"^\*+", line).end()
                if count > 1:
                    line = re.sub(r"^\*+", '-', line, 1)
                line = count*self.indent + line
            info.append(self.indent+line)
        return info

    def find_keybind(self, cmd):
        from pyful.filer import Directory

        key = []
        for k, v in Directory.keymap.items():
            if v == cmd:
                keybind = keymap.keyhelp[k[1]]
                if k[0]:
                    keybind = 'Meta + %s' % keybind
                if len(k) == 3:
                    keybind += ' (%s)' % k[2]
                key.append(self.indent+keybind)
        return key

    def show_command(self, name):
        from pyful.command import commands

        if not name:
            return
        if not name in commands:
            return message.error("Undefined command `%s'" % name)
        doc = commands[name].__doc__
        if not doc:
            return message.error("`%s' hasn't documentation" % name)

        info = []
        info.append(["Name:", curses.A_BOLD])
        info.append(self.indent+name)
        info.append('')

        key = self.find_keybind(commands[name])
        if key:
            info.append(["Keybinds:", curses.A_BOLD])
            info += key
            info.append('')

        info += self.parse_docstring(doc)
        self.show(info, -1)

    def show_all_command(self):
        from pyful.command import commands

        info = []
        for name, cmd in sorted(commands.items()):
            doc = cmd.__doc__
            if not doc:
                continue
            info.append(["Name:", curses.A_BOLD])
            info.append(self.indent+name)
            info.append('')

            key = self.find_keybind(commands[name])
            if key:
                info.append(["Keybinds:", curses.A_BOLD])
                info += key
                info.append('')

            info += self.parse_docstring(doc)
            info.append('-'*100)
        self.show(info, -1)
