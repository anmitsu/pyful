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

from pyful import look
from pyful import message
from pyful import ui
from pyful import util

class Help(ui.InfoBox):
    re_underline = re.compile(r"((?:[^+\\]|\\.)*)\s(\+(?:[^+\\]|\\.)*\+)\s")
    re_bold = re.compile(r"((?:[^*\\]|\\.)*)\s(\*(?:[^*\\]|\\.)*\*)\s")
    re_reverse = re.compile(r"((?:[^@\\]|\\.)*)\s(@(?:[^@\\]|\\.)*@)\s")
    re_prompt = re.compile(r"((?:[^$\\]|\\.)*)\s(\$(?:[^$\\]|\\.)*\$)\s")

    def __init__(self):
        ui.InfoBox.__init__(self, "Help")
        self.indent = ' ' * 4

    def parse_docstring(self, doc):
        info = []
        info.append(ui.InfoBoxContext("Documentation:", attr=curses.A_BOLD))
        level = 1
        number = 1
        for line in doc.split(os.linesep):
            line = line.strip()
            linebreak = False

            if line.startswith('*'):
                count = re.match(r"^\*+", line).end()
                if count > 1:
                    line = re.sub(r"^\*+", '-', line, 1)
                indent = (count-1+level)*self.indent
                attr = 0
            elif line.startswith('='):
                count = re.match(r"^=+", line).end()
                line = re.sub(r"^=+", '', line, 1).strip()
                indent = (count-1)*self.indent
                attr = curses.A_BOLD
                info.append(ui.InfoBoxContext(''))
                level = count
            elif line.startswith('#'):
                line = line.replace('#', '', 1).strip()
                line = '%s. %s' % (number, line)
                indent = level*self.indent
                attr = 0
                number += 1
            elif line.startswith('$'):
                info.append(ui.InfoBoxContext(''))
                line = line.replace('$', '', 1).strip()
                indent = (level+1)*self.indent
                attr = 0
                linebreak = True
            else:
                indent = level*self.indent
                attr = 0

            if self.re_underline.search(line):
                info.append(AttributeContext(line, indent, attr=attr, attrtype='underline'))
            elif self.re_bold.search(line):
                info.append(AttributeContext(line, indent, attr=attr, attrtype='bold'))
            elif self.re_reverse.search(line):
                info.append(AttributeContext(line, indent, attr=attr, attrtype='reverse'))
            elif self.re_prompt.search(line):
                info.append(AttributeContext(line, indent, attr=attr, attrtype='prompt'))
            else:
                info.append(ui.InfoBoxContext(indent+line, attr=attr))

            if linebreak:
                info.append(ui.InfoBoxContext(''))
        return info

    def find_keybind(self, cmd):
        from pyful.filer import Directory

        key = []
        for k, v in Directory.keymap.items():
            if v == cmd:
                keybind = curses.keyname(k[1])
                if keybind.isupper() and len(keybind) == 1:
                    keybind = 'Shift + %s' % keybind.lower()
                elif keybind.startswith('^'):
                    keybind = 'Control + %s' % keybind.lower().replace('^', '')
                elif keybind == ' ':
                    keybind = 'KEY_SPACE'

                if k[0]:
                    keybind = 'Meta + %s' % keybind
                if len(k) == 3:
                    keybind += ' (%s)' % k[2]
                key.append(ui.InfoBoxContext(self.indent+keybind))
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
        info.append(ui.InfoBoxContext("Name:", attr=curses.A_BOLD))
        info.append(ui.InfoBoxContext(self.indent+name))
        info.append(ui.InfoBoxContext(''))

        key = self.find_keybind(commands[name])
        if key:
            info.append(ui.InfoBoxContext("Keybinds:", attr=curses.A_BOLD))
            info += key
            info.append(ui.InfoBoxContext(''))

        info += self.parse_docstring(doc)
        self.show(info, -1)

    def show_all_command(self):
        from pyful.command import commands

        info = []
        for name, cmd in sorted(commands.items()):
            doc = cmd.__doc__
            if not doc:
                continue
            info.append(ui.InfoBoxContext("Name:", attr=curses.A_BOLD))
            info.append(ui.InfoBoxContext(self.indent+name))
            info.append(ui.InfoBoxContext(''))

            key = self.find_keybind(commands[name])
            if key:
                info.append(ui.InfoBoxContext("Keybinds:", attr=curses.A_BOLD))
                info += key
                info.append(ui.InfoBoxContext(''))

            info += self.parse_docstring(doc)
            info.append(ui.InfoBoxContext('-'*100))
        self.show(info, -1)

class AttributeContext(ui.InfoBoxContext):
    def __init__(self, string, indent, attr=0, attrtype='bold'):
        ui.InfoBoxContext.__init__(self, string, attr=attr)
        self.indent = indent
        if attrtype == 'bold':
            self.hiattr = curses.A_BOLD
            self.rematch = Help.re_bold
            self.symbol = '*'
        elif attrtype == 'underline':
            self.hiattr = curses.A_UNDERLINE
            self.rematch = Help.re_underline
            self.symbol = '+'
        elif attrtype == 'reverse':
            self.hiattr = curses.A_REVERSE
            self.rematch = Help.re_reverse
            self.symbol = '@'
        elif attrtype == 'prompt':
            self.hiattr = look.colors['CmdlinePrompt']
            self.rematch = Help.re_prompt
            self.symbol = '$'

    def addstr(self, win, width):
        string = util.mbs_ljust(self.string, width-len(self.indent))
        symbol = self.symbol
        win.addstr(self.indent, self.attr)
        for s in self.rematch.split(string):
            if s.startswith(symbol) and s.endswith(symbol):
                s = s.replace('\%s' % symbol, symbol)
                win.addstr(s.strip(symbol), self.attr | self.hiattr)
            else:
                win.addstr(s, self.attr)
