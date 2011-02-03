# cmdline.py - command line management
#
# Copyright (C) 2010 anmitsu <anmitsu.s@gmail.com>
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

import os
import re
import subprocess

from pyful import Pyful
from pyful import Singleton
from pyful import completion
from pyful import util
from pyful import look
from pyful import process
from pyful import ui
from pyful.message import Message
from pyful.keymap import *

class Cmdline(Singleton):
    keymap = {}
    wordbreakchars = re.compile("[._/\s\t\n\"\\`'@$><=:|&{(]")

    def __init_of_singleton__(self):
        self.string = ""
        self.cursor = 0
        self.active = False
        self._stringcue = []
        self.mode = None
        self.history = History(self)
        self.clipboard = Clipboard(self)
        self.output = Output(self)
        self.completion = completion.Completion(self)

        self.core = Pyful()
        self.message = Message()

    def execute(self):
        string = self.string
        if self.mode.__class__.__name__ == 'Shell':
            expand_string = util.expandmacro(self.string, shell=True)
        else:
            expand_string = util.expandmacro(self.string, shell=False)
        self.finish()
        self.history.append(string)
        self.mode.execute(expand_string)

    def expandmacro(self):
        if self.mode.__class__.__name__ == 'Shell':
            self.string = util.expandmacro(self.string, shell=True)
        else:
            self.string = util.expandmacro(self.string, shell=False)
        self.cursor += util.mbslen(self.string)
        self.history.restart()

    def escape(self):
        self.history.append(self.string)
        self.finish()

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = util.mbslen(self.string)

    def forward_char(self):
        self.cursor += 1

    def backward_char(self):
        self.cursor -= 1

    def forward_word(self):
        i = self.cursor + 1
        s = util.unistr(self.string)
        while i < util.mbslen(self.string):
            c = s[i]
            if self.wordbreakchars.search(c):
                break
            i += 1
        self.cursor = i

    def backward_word(self):
        if 0 >= self.cursor:
            return

        i = self.cursor - 1
        s = util.unistr(self.string)
        while 0 < i:
            c = s[i-1]
            if self.wordbreakchars.search(c):
                break
            i -= 1
        self.cursor = i

    def delete_backward_char(self):
        if not self.cursor:
            return
        self.string = util.rmstr(self.string, self.cursor-1)
        self.cursor -= 1
        self.history.restart()

    def delete_char(self):
        if not self.string:
            self.finish()
        self.string = util.rmstr(self.string, self.cursor)
        self.history.restart()

    def delete_forward_word(self):
        i = self.cursor + 1
        s = self.string
        while i < util.mbslen(self.string):
            c = s[i]
            if self.wordbreakchars.search(c):
                break
            i += 1
        delword = util.unistr(self.string)[self.cursor:i]
        self.clipboard.yank(delword)
        self.string = util.slicestr(self.string, self.cursor, i)
        self.history.restart()

    def delete_backward_word(self):
        if not self.cursor:
            return
        i = self.cursor - 1
        s = util.unistr(self.string)
        while 0 < i:
            c = s[i-1]
            if self.wordbreakchars.search(c):
                break
            i -= 1
        delword = util.unistr(self.string)[:self.cursor]
        self.clipboard.yank(delword)
        self.string = util.slicestr(self.string, i, self.cursor)
        self.cursor = i
        self.history.restart()

    def kill_line(self):
        self.string = util.unistr(self.string)
        killword = self.string[self.cursor:]
        self.clipboard.yank(killword)
        self.string = self.string[:self.cursor]
        self.history.restart()

    def kill_line_all(self):
        self.clipboard.yank(self.string)
        self.string = ""
        self.cursor = 0
        self.history.restart()

    def view(self):
        if self.completion.active:
            self.completion.view(maxrow=self.completion.maxrow)
        elif self.clipboard.active:
            self.clipboard.view()
        elif self.output.active:
            self.output.view()
        elif self.history.active:
            self.history.view()

        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor > util.mbslen(self.string):
            self.cursor = util.mbslen(self.string)

        self.core.stdscr.cmdwin.erase()
        self.core.stdscr.cmdwin.move(0, 0)
        prompt = " %s " % self.mode.prompt
        self.core.stdscr.cmdwin.addstr(prompt, look.colors['CMDLINE'])
        try:
            if self.mode.__class__.__name__ == "Shell":
                self.print_color_shell(self.string)
            elif self.mode.__class__.__name__ == "Eval":
                self.print_color_eval(self.string)
            else:
                self.print_color_default(self.string)
        except Exception as e:
            self.message.error("curses error: " + str(e))

        curpos = util.termwidth(prompt+self.string, util.mbslen(prompt)+self.cursor)
        if curpos < self.core.stdscr.maxx:
            self.core.stdscr.cmdwin.move(0, curpos)
        self.core.stdscr.cmdwin.noutrefresh()

    def input(self, meta, key):
        if self.completion.active:
            self.completion.input(meta, key)
        elif self.clipboard.active:
            self.clipboard.input(meta, key)
        elif self.output.active:
            self.output.input(meta, key)
        else:
            self.cmdline_input(meta, key)

    def finish(self):
        self.core.stdscr.cmdwin.erase()
        self.core.stdscr.cmdwin.noutrefresh()
        self.string = ""
        self.cursor = 0
        self.active = False

    def start(self, mode, string='', pos=0):
        self.mode = mode
        self.string = string
        if pos > 0:
            self.cursor = pos - 1
        else:
            self.cursor = util.mbslen(self.string) + pos
        self.active = True
        self.history.start()

    def restart(self, string='', pos=0):
        cmd = string
        self.string = cmd
        if pos > 0:
            self.cursor = pos - 1
        else:
            self.cursor = util.mbslen(cmd) + pos
        self.active = True
        self.history.start()

    def shell(self, string='', pos=0):
        from pyful import mode
        self.start(mode.Shell(), string, pos)

    def eval(self, string='', pos=0):
        from pyful import mode
        self.start(mode.Eval(), string, pos)

    def mx(self, string='', pos=0):
        from pyful import mode
        self.start(mode.Mx(), string, pos)

    def print_color_default(self, string):
        reg = re.compile("([\s;.()]|(?<!\\\\)%[mMdDfFxX])")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[mMdDfFxX]$", s):
                attr = look.colors['CMDLINEMACRO']
            self.core.stdscr.cmdwin.addstr(s, attr)

    def print_color_shell(self, string):
        prg = False
        reg = re.compile("([\s;|>]|[^%]&|(?<!\\\\)%[mMdDfFxX])")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[&TqmMdDfFxX]$", s):
                attr = look.colors['CMDLINEMACRO']
            elif re.search("^[;|>&]$", s):
                attr = look.colors['CMDLINESEPARATOR']
                prg = False
            elif s.startswith("-") and prg:
                attr = look.colors['CMDLINEOPTION']
            elif not s == "\s" and not prg:
                if s in self.completion.programs:
                    attr = look.colors['CMDLINEPROGRAM']
                    prg = True
                else:
                    attr = look.colors['CMDLINENOPROGRAM']
            self.core.stdscr.cmdwin.addstr(s, attr)

    def print_color_eval(self, string):
        reg = re.compile("([\s;.()]|(?<!\\\\)%[mMdDfFxX])")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[&TqmMdDfFxX]$", s):
                attr = look.colors['CMDLINEMACRO']
            elif re.search("^[;]$", s):
                attr = look.colors['CMDLINESEPARATOR']
            elif s in __builtins__.keys():
                attr = look.colors['CMDLINEPYFUNCTION']
            self.core.stdscr.cmdwin.addstr(s, attr)

    def cmdline_input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
        else:
            try:
                c = chr(key)
            except ValueError:
                return
            if c < " ":
                return
            try:
                s = util.unistr(c)
            except UnicodeError:
                self._stringcue.append(c)
                try:
                    s = util.unistr("".join(self._stringcue))
                    self._stringcue[:] = []
                except UnicodeError:
                    return
            length = util.mbslen(self.string)
            self.string = util.insertstr(self.string, s, self.cursor)
            self.cursor += util.mbslen(self.string) - length
            self.history.restart()

class History(ui.InfoBox):
    _maxsave = 10000
    def _get_maxsave(self):
        return self._maxsave
    def _set_maxsave(self, i):
        self.__class__._maxsave = i
    maxsave = property(_get_maxsave, _set_maxsave)

    _index = {}

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "history")
        self.cmdline = cmdline
        self.source = None

    def loadfile(self, path, key):
        try:
            with open(os.path.expanduser(path), "r") as f:
                for i, line in enumerate(f):
                    if self._maxsave <= i:
                        break
                    self.index(key).append(line.strip(os.linesep))
        except IOError:
            return

    def savefile(self, path, key):
        try:
            dirname = util.unix_dirname(os.path.expanduser(path))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(os.path.expanduser(path), "w") as f:
                for cmd in self.index(key):
                    f.write(cmd+os.linesep)
        except IOError:
            return

    def index(self, key):
        if not key in self._index:
            self.__class__._index[key] = []
        return self._index[key]

    def append(self, string):
        if not string:
            return
        li = self.index(self.cmdline.mode.__class__.__name__)
        if string in li:
            li.remove(string)
        if self._maxsave <= len(li):
            li.pop(0)
        li.append(string)

    def delete(self):
        li = self.index(self.cmdline.mode.__class__.__name__)
        try:
            li[self.cursor]
        except IndexError:
            return
        if not li or self.info is None:
            return

        if self.cursor_item() in li:
            li.remove(self.cursor_item())
        x = self.cursor
        if self.source:
            self.cmdline.string = self.source
        else:
            self.cmdline.string = ''
        self.start()
        self.setcursor(x)

    def restart(self):
        self.hide()
        self.source = None
        self.start()

    def start(self):
        self.source = None
        info = []
        for item in self.index(self.cmdline.mode.__class__.__name__):
            if self.cmdline.string in item:
                info.insert(0, item)
        if info:
            self.show(info, pos=-1, highlight=self.cmdline.string)
        else:
            self.hide()

    def mvcursor(self, x):
        if self.source is None:
            self.source = self.cmdline.string

        super(self.__class__, self).mvcursor(x)

        if self.cursor == -1:
            self.cmdline.string = self.source
            self.cmdline.cursor = util.mbslen(self.cmdline.string)
            self.source = None
        else:
            item = self.cursor_item()
            if item:
                self.cmdline.string = item
                self.cmdline.cursor = util.mbslen(self.cmdline.string)

class Clipboard(ui.InfoBox):
    _maxsave = 100
    def _get_maxsave(self):
        return self.__class__._maxsave
    def _set_maxsave(self, v):
        self.__class__._maxsave = v
    maxsave = property(_get_maxsave, _set_maxsave)

    clip = []

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "clipboard")
        self.cmdline = cmdline

    def loadfile(self, path):
        try:
            with open(os.path.expanduser(path), "r") as f:
                for i, line in enumerate(f):
                    if self._maxsave <= i:
                        break
                    self.__class__.clip.append(line.strip(os.linesep))
        except IOError:
            return

    def savefile(self, path):
        try:
            with open(os.path.expanduser(path), "w") as f:
                for c in self.__class__.clip:
                    f.write(c+os.linesep)
        except IOError:
            return

    def insert(self):
        item = self.cursor_item()
        self.cmdline.string = util.insertstr(self.cmdline.string, item, self.cmdline.cursor)
        self.cmdline.cursor += util.mbslen(item)
        self.hide()
        self.cmdline.history.start()

    def delete(self):
        if not self.clip:
            return
        self.__class__.clip.remove(self.cursor_item())
        c = self.cursor
        self.restart()
        self.setcursor(c)

    def yank(self, string):
        if not string:
            return
        string = util.unistr(string)

        if string in self.clip:
            self.__class__.clip.remove(string)
        if len(self.clip) >= self._maxsave:
            self.clip.pop(0)
        self.__class__.clip.append(string)

    def paste(self):
        if not self.clip:
            return
        item = self.clip[-1]
        self.cmdline.string = util.insertstr(self.cmdline.string, item, self.cmdline.cursor)
        self.cmdline.cursor += util.mbslen(item)

    def input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
        else:
            self.finish()
            self.cmdline.input(meta, key)

    def start(self):
        info = []
        for item in self.clip:
            info.insert(0, item)
        if info:
            self.cmdline.history.hide()
            self.show(info)

    def restart(self):
        self.hide()
        self.start()

    def finish(self):
        self.hide()
        self.cmdline.history.start()

class Output(ui.InfoBox):
    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "output")
        self.cmdline = cmdline

    def edit(self):
        try:
            li = self.cursor_item().split(":")
            fname = li[0]
            lnum = li[1]
            process.spawn("%s +%s %s" % (self.core.environs['EDITOR'], lnum, fname))
        except Exception as e:
            self.message.error("edit: %s" % str(e))

    def infoarea(self, string=None):
        from pyful import mode
        if not isinstance(self.cmdline.mode, mode.Shell):
            return
        if string is None:
            string = self.cmdline.string
        cmd = util.expandmacro(string)
        (out, err) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        info = (out + err)
        if info:
            self.cmdline.history.hide()
            reg = re.compile("[\r\t]")
            self.show([reg.sub("", item) for item in info.split(os.linesep) if item != ''])

    def terminal(self):
        pass

    def finish(self):
        self.hide()
        self.cmdline.history.start()

