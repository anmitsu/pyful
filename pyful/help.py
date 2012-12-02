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
import re

from pyful import look
from pyful import message
from pyful import util
from pyful import widget
from pyful import widgets

from pyful.widget.listbox import ListBox, Entry

class Help(ListBox):
    regexs = {
        "underline": re.compile(r"((?:[^+\\]|\\.)*)(?:\s|^)(\+(?:[^+\\]|\\.)*\+)(?:\s|$)"),
        "bold": re.compile(r"((?:[^*\\]|\\.)*)(?:\s|^)(\*(?:[^*\\]|\\.)*\*)(?:\s|$)"),
        "reverse": re.compile(r"((?:[^@\\]|\\.)*)(?:\s|^)(@(?:[^@\\]|\\.)*@)(?:\s|$)"),
        "prompt": re.compile(r"((?:[^$\\]|\\.)*)(?:\s|^)(\$(?:[^$\\]|\\.)*\$)(?:\s|$)"),
        }

    def __init__(self):
        ListBox.__init__(self, "Help")
        self.indent = " " * 4

    def parse_docstring(self, doc):
        entries = []
        entries.append(Entry("Documentation:", attr=curses.A_BOLD))
        level = 1
        number = 1
        for line in doc.splitlines():
            line = line.strip()
            linebreak = False

            if line.startswith("*"):
                count = re.match(r"^\*+", line).end()
                if count > 1:
                    line = re.sub(r"^\*+", "-", line, 1)
                indent = (count-1+level)*self.indent
                attr = 0
            elif line.startswith("="):
                count = re.match(r"^=+", line).end()
                line = re.sub(r"^=+", "", line, 1).strip()
                indent = (count-1)*self.indent
                attr = curses.A_BOLD
                entries.append(Entry(""))
                level = count
            elif line.startswith("#"):
                line = line.replace("#", "", 1).strip()
                line = "{0}. {1}".format(number, line)
                indent = level*self.indent
                attr = 0
                number += 1
            elif line.startswith("$"):
                entries.append(Entry(""))
                line = line.replace("$", "", 1).strip()
                indent = (level+1)*self.indent
                attr = 0
                linebreak = True
            else:
                indent = level*self.indent
                attr = 0

            if self.regexs["underline"].search(line):
                entries.append(AttributeEntry(line, indent, attr=attr, attrtype="underline"))
            elif self.regexs["bold"].search(line):
                entries.append(AttributeEntry(line, indent, attr=attr, attrtype="bold"))
            elif self.regexs["reverse"].search(line):
                entries.append(AttributeEntry(line, indent, attr=attr, attrtype="reverse"))
            elif self.regexs["prompt"].search(line):
                entries.append(AttributeEntry(line, indent, attr=attr, attrtype="prompt"))
            else:
                entries.append(Entry(indent+line, attr=attr))

            if linebreak:
                entries.append(Entry(""))
        return entries

    def find_keybind(self, cmd):
        keys = []
        for k, v in widgets.filer.keymap.items():
            if v == cmd:
                if isinstance(k, tuple):
                    keybind = "{0[0]} ({0[1]})".format(k)
                else:
                    keybind = k
                keys.append(Entry(self.indent+keybind))
        return keys

    def show_command(self, name):
        from pyful.command import commands

        if not name:
            return
        if not name in commands:
            return message.error("Undefined command `{0}'".format(name))
        doc = commands[name].__doc__
        if not doc:
            return message.error("`{0}' hasn't documentation".format(name))

        entries = []
        entries.append(Entry("Name:", attr=curses.A_BOLD))
        entries.append(Entry(self.indent+name))
        entries.append(Entry(""))

        keys = self.find_keybind(commands[name])
        if keys:
            entries.append(Entry("Keybinds:", attr=curses.A_BOLD))
            entries.extend(keys)
            entries.append(Entry(""))

        entries.extend(self.parse_docstring(doc))
        self.show(entries)

    def show_all_command(self):
        from pyful.command import commands

        entries = []
        for name, cmd in sorted(commands.items()):
            doc = cmd.__doc__
            if not doc:
                continue
            entries.append(Entry("Name:", attr=curses.A_BOLD))
            entries.append(Entry(self.indent+name))
            entries.append(Entry(""))

            keys = self.find_keybind(commands[name])
            if keys:
                entries.append(Entry("Keybinds:", attr=curses.A_BOLD))
                entries.extend(keys)
                entries.append(Entry(""))

            entries.extend(self.parse_docstring(doc))
            entries.append(Entry("-"*100))
        self.show(entries)

class AttributeEntry(Entry):
    def __init__(self, text, indent, attr=0, attrtype="bold"):
        Entry.__init__(self, text, attr=attr)
        self.indent = indent
        if attrtype == "bold":
            self.hiattr = curses.A_BOLD
            self.rematch = Help.regexs["bold"]
            self.symbol = "*"
        elif attrtype == "underline":
            self.hiattr = curses.A_UNDERLINE
            self.rematch = Help.regexs["underline"]
            self.symbol = "+"
        elif attrtype == "reverse":
            self.hiattr = curses.A_REVERSE
            self.rematch = Help.regexs["reverse"]
            self.symbol = "@"
        elif attrtype == "prompt":
            self.hiattr = look.colors["CmdlinePrompt"]
            self.rematch = Help.regexs["prompt"]
            self.symbol = "$"

    def addstr(self, win, width):
        text = util.mbs_ljust(self.text, width-len(self.indent))
        symbol = self.symbol
        win.addstr(self.indent, self.attr)
        for s in self.rematch.split(text):
            if s.startswith(symbol) and s.endswith(symbol):
                s = s.replace("\{0}".format(symbol), symbol)
                win.addstr(s.strip(symbol), self.attr | self.hiattr)
            else:
                win.addstr(s, self.attr)
