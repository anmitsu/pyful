# cmdline.py - command line management
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
import subprocess
import unicodedata

from pyful import Pyful
from pyful import completion
from pyful import look
from pyful import message
from pyful import process
from pyful import ui
from pyful import util

class Cmdline(ui.Component):
    keymap = {}
    wordbreakchars = re.compile("[._/\s\t\n\"\\`'@$><=:|&{(]")

    def __init__(self):
        ui.Component.__init__(self, "Cmdline")
        self.string = ""
        self.cursor = 0
        self.mode = None
        self.history = History(self)
        self.clipboard = Clipboard(self)
        self.output = Output(self)
        self.completion = completion.Completion(self)

    def execute(self):
        string = self.string
        if self.mode.__class__.__name__ == "Shell":
            expand_string = util.expandmacro(self.string, shell=True)
        else:
            expand_string = util.expandmacro(self.string, shell=False)
        self.finish()
        self.history.append(string)
        self.mode.execute(expand_string)

    def expandmacro(self):
        if self.mode.__class__.__name__ == "Shell":
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
        s = util.U(self.string)
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
        s = util.U(self.string)
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
        delword = util.U(self.string)[self.cursor:i]
        self.clipboard.yank(delword)
        self.string = util.slicestr(self.string, self.cursor, i)
        self.history.restart()

    def delete_backward_word(self):
        if not self.cursor:
            return
        i = self.cursor - 1
        s = util.U(self.string)
        while 0 < i:
            c = s[i-1]
            if self.wordbreakchars.search(c):
                break
            i -= 1
        delword = util.U(self.string)[:self.cursor]
        self.clipboard.yank(delword)
        self.string = util.slicestr(self.string, i, self.cursor)
        self.cursor = i
        self.history.restart()

    def kill_line(self):
        self.string = util.U(self.string)
        killword = self.string[self.cursor:]
        self.clipboard.yank(killword)
        self.string = self.string[:self.cursor]
        self.history.restart()

    def kill_line_all(self):
        self.clipboard.yank(self.string)
        self.string = ""
        self.cursor = 0
        self.history.restart()

    def _get_current_line(self, win):
        maxy, maxx = win.getmaxyx()
        prompt = " {0} ".format(self.mode.prompt)
        promptlen = util.termwidth(prompt)
        if promptlen > maxx:
            prompt = util.mbs_ljust(prompt, maxx-2)
            promptlen = util.termwidth(prompt)
        self.string = util.U(self.string)
        realcurpos = util.termwidth(self.string[:self.cursor])
        if maxx <= util.termwidth(self.string)+promptlen:
            if maxx <= realcurpos+promptlen:
                width = promptlen
                start = 0
                pages = []
                for i, c in enumerate(self.string):
                    if unicodedata.east_asian_width(c) in "WF":
                        add = 2
                    else:
                        add = 1
                    width += add
                    if maxx <= width:
                        pages.append(self.string[start:i])
                        start = i
                        width = add
                pages.append(self.string[start:])

                string = ""
                for i, s in enumerate(pages):
                    curpos = realcurpos-util.termwidth(string)
                    string = "".join([string, s])
                    if self.cursor <= util.mbslen(string):
                        return ("", pages[i], curpos)
            else:
                cmd = util.mbs_ljust(self.string, maxx-promptlen+1, pad="")
                curpos = realcurpos+promptlen
                return (prompt, cmd, curpos)
        else:
            return (prompt, self.string, realcurpos+promptlen)

    def view(self):
        if self.completion.active:
            self.completion.view()
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

        cmdscr = ui.getcomponent("Cmdscr").win
        cmdscr.erase()
        cmdscr.move(0, 0)
        prompt, cmd, curpos = self._get_current_line(cmdscr)

        cmdscr.addstr(prompt, look.colors["CmdlinePrompt"])
        try:
            if self.mode.__class__.__name__ == "Shell":
                self.print_color_shell(cmd)
            elif self.mode.__class__.__name__ == "Eval":
                self.print_color_eval(cmd)
            else:
                self.print_color_default(cmd)
        except curses.error as e:
            message.error("curses error: " + str(e))
        cmdscr.move(0, curpos)
        cmdscr.noutrefresh()

    def input(self, key):
        if self.completion.active:
            self.completion.input(key)
        elif self.clipboard.active:
            self.clipboard.input(key)
        elif self.output.active:
            self.output.input(key)
        else:
            self.cmdline_input(key)

    def finish(self):
        cmdscr = ui.getcomponent("Cmdscr").win
        cmdscr.erase()
        cmdscr.noutrefresh()
        self.string = ""
        self.cursor = 0
        self.active = False

    def start(self, mode, string="", pos=0):
        self.mode = mode
        self.string = string
        if pos > 0:
            self.cursor = pos - 1
        else:
            self.cursor = util.mbslen(self.string) + pos
        self.active = True
        self.history.start()

    def restart(self, string="", pos=0):
        self.start(self.mode, string, pos)

    def shell(self, string="", pos=0):
        from pyful import mode
        self.start(mode.Shell(), string, pos)

    def eval(self, string="", pos=0):
        from pyful import mode
        self.start(mode.Eval(), string, pos)

    def mx(self, string="", pos=0):
        from pyful import mode
        self.start(mode.Mx(), string, pos)

    def print_color_default(self, string):
        cmdscr = ui.getcomponent("Cmdscr").win
        reg = re.compile(r"([\s;.()]|(?<!\\)%(?:[mMfFxX]|[dD]2?))")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[&TqmMfFxX]|[dD]2?$", s):
                attr = look.colors["CmdlineMacro"]
            cmdscr.addstr(s, attr)

    def print_color_shell(self, string):
        cmdscr = ui.getcomponent("Cmdscr").win
        prg = False
        reg = re.compile(r"([\s;|>]|[^%]&|(?<!\\)%(?:[mMfFxX]|[dD]2?))")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[&TqmMfFxX]|[dD]2?$", s):
                attr = look.colors["CmdlineMacro"]
            elif re.search("^[;|>&]$", s):
                attr = look.colors["CmdlineSeparator"]
                prg = False
            elif s.startswith("-") and prg:
                attr = look.colors["CmdlineOptions"]
            elif not s == "\s" and not prg:
                if s in self.completion.programs:
                    attr = look.colors["CmdlineProgram"]
                    prg = True
                else:
                    attr = look.colors["CmdlineNoProgram"]
            cmdscr.addstr(s, attr)

    def print_color_eval(self, string):
        cmdscr = ui.getcomponent("Cmdscr").win
        reg = re.compile(r"([\s;.()]|(?<!\\)%(?:[mMfFxX]|[dD]2?))")
        for s in reg.split(string):
            attr = 0
            if re.search("^%[&TqmMfFxX]|[dD]2?$", s):
                attr = look.colors["CmdlineMacro"]
            elif re.search("^[;]$", s):
                attr = look.colors["CmdlineSeparator"]
            elif s in __builtins__.keys():
                attr = look.colors["CmdlinePythonFunction"]
            cmdscr.addstr(s, attr)

    def cmdline_input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            if key == "SPC":
                key = " "
            if util.mbslen(key) == 1:
                self.string = util.insertstr(self.string, key, self.cursor)
                self.cursor += 1
                self.history.restart()

class History(ui.InfoBox):
    maxsave = 10000
    histories = {}

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "History")
        self.cmdline = cmdline
        self.source_string = self.cmdline.string

    def loadfile(self, path, key):
        path = os.path.expanduser(path)
        try:
            with open(path, "r") as f:
                for i, line in enumerate(f):
                    if self.maxsave <= i:
                        break
                    self.gethistory(key).append(line.strip(os.linesep))
        except IOError:
            return

    def savefile(self, path, key):
        path = os.path.expanduser(path)
        dirname = util.unix_dirname(path)
        try:
            os.makedirs(dirname)
        except OSError:
            pass
        try:
            with open(path, "w") as f:
                f.write("\n".join(self.gethistory(key)))
        except IOError:
            return

    def gethistory(self, key=None):
        if key is None:
            key = self.cmdline.mode.__class__.__name__
        if not key in self.histories:
            self.histories[key] = []
        return self.histories[key]

    def append(self, string):
        if not string:
            return
        history = self.gethistory()
        if string in history:
            history.remove(string)
        if self.maxsave <= len(history):
            history.pop(0)
        history.append(string)

    def delete(self):
        history = self.gethistory()
        if not history or not self.info or not 0 <= self.cursor < len(history):
            return
        item = self.cursor_item()
        if item.string in history:
            history.remove(item.string)
        x = self.cursor
        self.cmdline.string = self.source_string
        self.start()
        self.setcursor(x)

    def restart(self):
        self.hide()
        self.start()

    def start(self):
        self.source_string = self.cmdline.string
        t = self.cmdline.string
        info = [ui.InfoBoxContext(item, histr=t) for item in self.gethistory() if t in item]
        info.reverse()
        if info:
            self.show(info, pos=-1)
        else:
            self.hide()

    def mvcursor(self, x):
        if not self.info:
            return
        super(self.__class__, self).mvcursor(x)
        if self.cursor == -1:
            self.cmdline.string = self.source_string
            self.cmdline.cursor = util.mbslen(self.source_string)
        else:
            item = self.cursor_item()
            if item:
                self.cmdline.string = item.string
                self.cmdline.cursor = util.mbslen(item.string)

class Clipboard(ui.InfoBox):
    maxsave = 100
    clip = []

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "Clipboard")
        self.cmdline = cmdline

    def loadfile(self, path):
        path = os.path.expanduser(path)
        try:
            with open(path, "r") as f:
                for i, line in enumerate(f):
                    if self.maxsave <= i:
                        break
                    self.clip.append(line.strip(os.linesep))
        except IOError:
            return

    def savefile(self, path):
        path = os.path.expanduser(path)
        dirname = util.unix_dirname(path)
        try:
            os.makedirs(dirname)
        except OSError:
            pass
        try:
            with open(path, "w") as f:
                f.write("\n".join(self.clip))
        except IOError:
            return

    def insert(self):
        item = self.cursor_item()
        self.cmdline.string = util.insertstr(self.cmdline.string, item.string, self.cmdline.cursor)
        self.cmdline.cursor += util.mbslen(item.string)
        self.hide()
        self.cmdline.history.start()

    def delete(self):
        if not self.clip or not 0 < self.cursor <= len(self.clip):
            return
        self.clip.remove(self.cursor_item().string)
        x = self.cursor
        self.restart()
        self.setcursor(x)

    def yank(self, string):
        if not string:
            return
        if string in self.clip:
            self.clip.remove(string)
        if len(self.clip) >= self.maxsave:
            self.clip.pop(0)
        self.clip.append(string)

    def paste(self):
        if not self.clip:
            return
        item = self.clip[-1]
        self.cmdline.string = util.insertstr(self.cmdline.string, item, self.cmdline.cursor)
        self.cmdline.cursor += util.mbslen(item)

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            self.finish()
            self.cmdline.input(key)

    def start(self):
        info = [ui.InfoBoxContext(item) for item in self.clip]
        info.reverse()
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
        ui.InfoBox.__init__(self, "Output")
        self.cmdline = cmdline

    def edit(self):
        grepoutputs = self.cursor_item().string.split(":")
        fname = grepoutputs[0]
        lnum = grepoutputs[1]
        try:
            process.spawn("{0} +{1} {2}".format(Pyful.environs["EDITOR"], lnum, fname))
        except Exception as e:
            message.exception(e)

    def infoarea(self, string=None):
        if self.cmdline.mode.__class__.__name__ != "Shell":
            return
        if string is None:
            string = self.cmdline.string
        cmd = util.expandmacro(string)
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
        try:
            outputs = (out+err).decode()
        except UnicodeError:
            outputs = "Invalid encoding error: {0}".format(cmd)
        if not outputs:
            return
        self.cmdline.history.hide()
        info = []
        outputs = re.sub(r"[\r\t]", "", outputs)
        info = [ui.InfoBoxContext(item) for item in outputs.split(os.linesep)]
        self.show(info)

    def terminal(self):
        pass

    def finish(self):
        self.hide()
        self.cmdline.history.start()
