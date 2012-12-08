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

from pyful.widget.base import Widget

class TextBox(Widget):
    promptattr = 0
    wordbreakchars = re.compile("[._/\s\t\n\"\\`'@$><=:|&{(]")
    keymap = None

    def __init__(self, name=None):
        Widget.__init__(self, name)
        self.panel.leaveok = False
        self.text = ""
        self.textmap = []
        self.prompt = ""
        self.cursor = 0

    def refresh(self):
        self.panel.unlink_window()
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(2, x, y-2, 0)
        self.panel.attr = look.colors["TextBoxWindow"]
        self.promptattr = look.colors["CmdlinePrompt"]

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
        if not self.text or self.cursor <= 0:
            return
        self.text = util.rmstr(self.text, self.cursor-1)
        self.cursor -= 1
        del self.textmap[self.cursor]
        self.edithook()

    def delete_char(self):
        if not self.text:
            self.hide()
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

    def show(self):
        self.panel.show()

    def hide(self):
        self.panel.hide()
        self.text = ""
        self.textmap[:] = []
        self.cursor = 0

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

    def draw_prompt(self, prompt):
        self.panel.win.addstr(prompt, self.promptattr)

    def draw_text(self, text):
        self.panel.win.addstr(text)

    def draw(self):
        self.panel.create_window()
        self._fix_position()
        win = self.panel.win
        win.erase()
        win.move(0, 0)
        prompt, text, pos = self._get_current_line(win)
        self.draw_prompt(prompt)
        self.draw_text(text)
        win.move(0, pos)
        win.noutrefresh()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            if key == "SPC":
                self.insert(" ")
            elif util.mbslen(key) == 1:
                self.insert(key)
