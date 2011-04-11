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
import unicodedata

from pyful import look
from pyful import util
from pyful.widget import base

class TextBox(base.Widget):
    win = None
    winattr = 0
    promptattr = 0
    wordbreakchars = re.compile("[._/\s\t\n\"\\`'@$><=:|&{(]")

    def __init__(self, name, register=True):
        base.Widget.__init__(self, name, register)
        self.text = ""
        self.textmap = []
        self.prompt = ""
        self.cursor = 0
        self.y = self.x = self.begy = self.begx = 1
        self.keymap = {
            "C-f"         : self.forward_char,
            "<right>"     : self.forward_char,
            "C-b"         : self.backward_char,
            "<left>"      : self.backward_char,
            "M-f"         : self.forward_word,
            "M-b"         : self.backward_word,
            "C-d"         : self.delete_char,
            "<dc>"        : self.delete_char,
            "C-h"         : self.delete_backward_char,
            "<backspace>" : self.delete_backward_char,
            "M-d"         : self.delete_forward_word,
            "M-h"         : self.delete_backward_word,
            "C-w"         : self.delete_backward_word,
            "C-k"         : self.kill_line,
            "C-u"         : self.kill_line_all,
            "C-a"         : self.settop,
            "C-e"         : self.setbottom,
            "C-g"         : self.finish,
            "C-c"         : self.finish,
            "ESC"         : self.finish,
            }

    def resize(self):
        self.win = None
        y, x = self.stdscr.getmaxyx()
        self.y = 1
        self.x = x
        self.begy = y - 2
        self.begx = 0
        self.winattr = look.colors["TextBoxWindow"]
        self.promptattr = 0

    def edithook(self):
        pass

    def yankhook(self, yanked):
        pass

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = util.mbslen(self.text)

    def forward_char(self):
        self.cursor += 1

    def backward_char(self):
        self.cursor -= 1

    def forward_word(self):
        i = self.cursor + 1
        s = util.U(self.text)
        while i < len(s):
            if self.wordbreakchars.search(s[i]):
                break
            i += 1
        self.cursor = i

    def backward_word(self):
        if 0 >= self.cursor:
            return
        i = self.cursor - 1
        s = util.U(self.text)
        while 0 < i:
            if self.wordbreakchars.search(s[i-1]):
                break
            i -= 1
        self.cursor = i

    def delete_backward_char(self):
        if not self.text:
            return
        self.text = util.rmstr(self.text, self.cursor-1)
        self.cursor -= 1
        del self.textmap[self.cursor]
        self.edithook()

    def delete_char(self):
        if not self.text:
            self.finish()
        try:
            self.text = util.rmstr(self.text, self.cursor)
            del self.textmap[self.cursor]
            self.edithook()
        except IndexError:
            pass

    def delete_forward_word(self):
        i = self.cursor + 1
        s = util.U(self.text)
        while i < len(s):
            if self.wordbreakchars.search(s[i]):
                break
            i += 1
        delword = s[self.cursor:i]
        self.text = util.slicestr(self.text, self.cursor, i)
        del self.textmap[self.cursor:i]
        self.edithook()
        self.yankhook(delword)

    def delete_backward_word(self):
        if not self.cursor:
            return
        i = self.cursor - 1
        s = util.U(self.text)
        while 0 < i:
            if self.wordbreakchars.search(s[i-1]):
                break
            i -= 1
        delword = s[i:self.cursor]
        self.text = util.slicestr(self.text, i, self.cursor)
        del self.textmap[i:self.cursor]
        self.cursor = i
        self.edithook()
        self.yankhook(delword)

    def kill_line(self):
        self.text = util.U(self.text)
        killword = self.text[self.cursor:]
        self.text = self.text[:self.cursor]
        del self.textmap[self.cursor:]
        self.edithook()
        self.yankhook(killword)

    def kill_line_all(self):
        killword = self.text
        self.text = ""
        self.textmap[:] = []
        self.cursor = 0
        self.edithook()
        self.yankhook(killword)

    def insert(self, text):
        text = util.U(text)
        self.text = util.insertstr(self.text, text, self.cursor)
        self.text = util.U(self.text)
        for i, c in enumerate(text):
            if unicodedata.east_asian_width(c) in "WF":
                self.textmap.insert(self.cursor+i, 2)
            else:
                self.textmap.insert(self.cursor+i, 1)
        self.cursor += len(text)
        self.edithook()

    def settext(self, text):
        self.text = util.U(text)
        self.cursor = len(self.text)
        self.textmap[:] = []
        for c in self.text:
            if unicodedata.east_asian_width(c) in "WF":
                self.textmap.append(2)
            else:
                self.textmap.append(1)

    def finish(self):
        self.win = None
        self.text = ""
        self.textmap[:] = []
        self.prompt = ""
        self.cursor = 0
        self.active = False

    def create_window(self):
        if not self.win:
            self.win = curses.newwin(self.y, self.x, self.begy, self.begx)
            self.win.bkgd(self.winattr)

    def _get_current_line(self, win):
        y, x = win.getmaxyx()
        prompt = self.prompt
        promptlen = util.termwidth(prompt)
        if promptlen > x:
            prompt = util.mbs_ljust(prompt, x-4)
            promptlen = util.termwidth(prompt)
        realpos = sum(self.textmap[:self.cursor])
        if x-promptlen <= sum(self.textmap):
            if x-promptlen <= realpos+1:
                width = start = 0
                for i, count in enumerate(self.textmap):
                    width += count
                    if x-promptlen <= width:
                        if self.cursor < i:
                            pos = realpos - sum(self.textmap[:start]) + promptlen
                            return (prompt, self.text[start:i], pos)
                        start = i
                        width = count
                        prompt = "..."
                        promptlen = len(prompt)
                pos = realpos - sum(self.textmap[:start]) + promptlen
                return (prompt, self.text[start:], pos)
            else:
                text = util.mbs_ljust(self.text, x-promptlen)
                pos = realpos + promptlen
                return (prompt, text, pos)
        else:
            return (prompt, self.text, realpos+promptlen)

    def _fix_position(self):
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor > len(self.text):
            self.cursor = len(self.text)

    def view_prompt(self, prompt):
        self.win.addstr(prompt, self.promptattr)

    def view_text(self, text):
        self.win.addstr(text)

    def view(self):
        self.create_window()
        self._fix_position()
        self.win.erase()
        self.win.move(0, 0)
        prompt, text, pos = self._get_current_line(self.win)
        self.view_prompt(prompt)
        self.view_text(text)
        self.win.move(0, pos)
        self.win.noutrefresh()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            if key == "SPC":
                self.insert(" ")
            elif util.mbslen(key) == 1:
                self.insert(key)
