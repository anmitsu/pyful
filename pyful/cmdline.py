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
import keyword
import os
import re
import subprocess
import unicodedata

from pyful import Pyful
from pyful import completion
from pyful import look
from pyful import mode
from pyful import message
from pyful import process
from pyful import ui
from pyful import util

class Cmdline(ui.TextBox):
    def __init__(self):
        ui.TextBox.__init__(self, "Cmdline")
        self.mode = None
        self.history = History(self)
        self.clipboard = Clipboard(self)
        self.output = Output(self)
        self.completion = completion.Completion(self)

    def resize(self):
        self.win = None
        y, x = self.stdscr.getmaxyx()
        self.y = 2
        self.x = x
        self.begy = y - 2
        self.begx = 0
        self.winattr = look.colors["CmdlineWindow"]
        self.promptattr = look.colors["CmdlinePrompt"]

    def edithook(self):
        self.history.start()

    def yankhook(self, yanked):
        self.clipboard.yank(yanked)

    def view_text(self, text):
        if self.mode.__class__.__name__ == "Shell":
            self.print_color_shell(self.win, text)
        elif self.mode.__class__.__name__ == "Eval":
            self.print_color_eval(self.win, text)
        else:
            self.print_color_default(self.win, text)

    def view(self):
        if self.completion.active:
            self.completion.view()
        elif self.clipboard.active:
            self.clipboard.view()
        elif self.output.active:
            self.output.view()
        elif self.history.active:
            self.history.view()
        super(self.__class__, self).view()

    def input(self, key):
        if self.completion.active:
            self.completion.input(key)
        elif self.clipboard.active:
            self.clipboard.input(key)
        elif self.output.active:
            self.output.input(key)
        else:
            super(self.__class__, self).input(key)

    def start(self, mode, text="", pos=-1):
        self.mode = mode
        self.settext(text)
        self.prompt = "{1[0]}{0}{1[1]}".format(self.mode.prompt, self.mode.prompt_side)
        if pos >= 0:
            self.cursor = pos
        else:
            self.cursor = util.mbslen(self.text) + 1 + pos
        self.active = True
        self.edithook()

    def restart(self, text="", pos=-1):
        self.start(self.mode, text, pos)

    def shell(self, text="", pos=-1):
        self.start(mode.Shell(), text, pos)

    def eval(self, text="", pos=-1):
        self.start(mode.Eval(), text, pos)

    def mx(self, text="", pos=-1):
        self.start(mode.Mx(), text, pos)

    def execute(self, action=None):
        text = self.text
        if self.mode.__class__.__name__ == "Shell":
            expanded = util.expandmacro(self.text, shell=True)
        else:
            expanded = util.expandmacro(self.text, shell=False)
        self.finish()
        self.history.append(text)
        ret = self.mode.execute(expanded, action)
        if isinstance(ret, (tuple, list)) and len(ret) == 2:
            self.restart(ret[0], ret[1])

    def expandmacro(self):
        if self.mode.__class__.__name__ == "Shell":
            self.settext(util.expandmacro(self.text, shell=True))
        else:
            self.settext(util.expandmacro(self.text, shell=False))
        self.edithook()

    def escape(self):
        self.history.append(self.text)
        self.finish()

    def select_action(self):
        action = self.mode.select_action()
        if action:
            self.execute(action)

    def print_color_default(self, win, text):
        for s in re.split(r"(?<!\\)(%(?:[mMfFxX]|[dD]2?))", text):
            attr = 0
            if re.search("^%(?:[mMfFxX]|[dD]2?)$", s):
                attr = look.colors["CmdlineMacro"]
            win.addstr(s, attr)

    def print_color_shell(self, win, text):
        prg = False
        for s in re.split(r"(?<!\\)([\s;|>&]|%(?:[&TqmMfFxX]|[dD]2?))", text):
            attr = 0
            if re.search("^%(?:[&TqmMfFxX]|[dD]2?)$", s):
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
            win.addstr(s, attr)

    def print_color_eval(self, win, text):
        for s in re.split(r"(?<!\\)([\s;.()]|%(?:[&TqmMfFxX]|[dD]2?))", text):
            attr = 0
            if re.search("^%(?:[&TqmMfFxX]|[dD]2?)$", s):
                attr = look.colors["CmdlineMacro"]
            elif re.search("^;$", s):
                attr = look.colors["CmdlineSeparator"]
            elif s in __builtins__ or s in keyword.kwlist:
                attr = look.colors["CmdlinePythonFunction"]
            win.addstr(s, attr)

class History(ui.InfoBox):
    maxsave = 10000
    histories = {}

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "History")
        self.cmdline = cmdline
        self.source_string = self.cmdline.text
        self.lb = -1

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
        self.cmdline.settext(self.source_string)
        self.start()
        self.setcursor(x)

    def start(self):
        self.source_string = self.cmdline.text
        t = self.cmdline.text
        info = [ui.InfoBoxContext(item, histr=t) for item in self.gethistory() if t in item]
        info.reverse()
        if info:
            self.show(info)
        else:
            self.hide()

    def mvcursor(self, x):
        if not self.info:
            return
        super(self.__class__, self).mvcursor(x)
        if self.cursor == self.lb:
            self.cmdline.settext(self.source_string)
        else:
            item = self.cursor_item()
            if item:
                self.cmdline.settext(item.string)

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
        self.cmdline.insert(item.string)
        self.finish()

    def delete(self):
        item = self.cursor_item()
        if item:
            self.clip.remove(item.string)
        x = self.cursor
        self.start()
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
        self.cmdline.insert(item)
        self.finish()

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
        else:
            self.hide()

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
            string = self.cmdline.text
        cmd = util.expandmacro(string)
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
        info = []
        for line in (out + err).splitlines():
            try:
                line = line.decode()
                line = re.sub(r"[\r]", "", line).expandtabs()
                attr = 0
            except UnicodeError:
                line = "????? - Invalid encoding"
                attr = look.colors["ErrorMessage"]
            info.append(ui.InfoBoxContext(line, attr=attr))
        self.show(info)

    def terminal(self):
        pass

    def finish(self):
        self.hide()
        self.cmdline.history.start()
