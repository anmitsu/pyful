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

import keyword
import os
import re
import subprocess

from pyful import Pyful
from pyful import completion
from pyful import look
from pyful import mode
from pyful import message
from pyful import process
from pyful import util

from pyful.widget.textbox import TextBox
from pyful.widget.listbox import ListBox, Entry

class Cmdline(TextBox):
    def __init__(self):
        TextBox.__init__(self, "Cmdline")
        self.mode = None
        self.history = History(self)
        self.clipboard = Clipboard(self)
        self.output = Output(self)
        self.completion = completion.Completion(self)

    def refresh(self):
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(2, x, y-2, 0)
        self.panel.attr = look.colors["CmdlineWindow"]
        self.promptattr = look.colors["CmdlinePrompt"]
        self.history.refresh()
        self.clipboard.refresh()
        self.output.refresh()
        self.completion.refresh()

    def edithook(self):
        self.history.start()

    def yankhook(self, yanked):
        self.clipboard.yank(yanked)

    def draw_text(self, text):
        if self.mode.__class__.__name__ == "Shell":
            self.print_color_shell(self.panel.win, text)
        elif self.mode.__class__.__name__ == "Eval":
            self.print_color_eval(self.panel.win, text)
        else:
            self.print_color_default(self.panel.win, text)

    def draw(self):
        super(self.__class__, self).draw()
        if self.completion.active:
            self.completion.draw()
        elif self.clipboard.active:
            self.clipboard.draw()
        elif self.output.active:
            self.output.draw()
        elif self.history.active:
            self.history.draw()

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
        self.show()
        self.prompt = self.mode.prompt
        if pos >= 0:
            self.cursor = pos
        else:
            self.cursor = util.mbslen(self.text) + 1 + pos
        self.history.start()

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
        self.hide()
        self.history.append(text)
        self.history.hide()
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
        self.history.hide()
        self.hide()

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

class History(ListBox):
    maxsave = 10000
    histories = {}

    def __init__(self, cmdline):
        ListBox.__init__(self)
        self.title = "history"
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
        if not string or string.startswith(" "):
            return
        history = self.gethistory()
        try:
            history.remove(string)
        except ValueError:
            pass
        if self.maxsave <= len(history):
            history.pop(0)
        history.append(string)

    def delete(self):
        history = self.gethistory()
        entry = self.cursor_entry()
        try:
            history.remove(entry.text)
        except ValueError:
            return
        x = self.cursor
        self.cmdline.settext(self.source_string)
        self.start()
        self.setcursor(x)

    def start(self):
        self.source_string = self.cmdline.text
        t = self.cmdline.text
        entries = [Entry(item, histr=t) for item in self.gethistory() if t in item]
        entries.reverse()
        if entries:
            self.show(entries)
        else:
            self.hide()

    def mvcursor(self, x):
        super(self.__class__, self).mvcursor(x)
        if self.cursor == self.lb:
            self.cmdline.settext(self.source_string)
        else:
            entry = self.cursor_entry()
            if entry.text:
                self.cmdline.settext(entry.text)

class Clipboard(ListBox):
    maxsave = 100
    clip = []

    def __init__(self, cmdline):
        ListBox.__init__(self)
        self.title = "clipboard"
        self.cmdline = cmdline
        self.textbox = TextBox()
        self.textbox.prompt = " Clipboard: "
        self.textbox.edithook = self.start

    def refresh(self):
        self.textbox.refresh()
        super(self.__class__, self).refresh()

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
        entry = self.cursor_entry()
        self.cmdline.insert(entry.text)
        self.finish()

    def delete(self):
        entry = self.cursor_entry()
        try:
            self.clip.remove(entry.text)
        except ValueError:
            return
        x = self.cursor
        self.start()
        self.setcursor(x)

    def yank(self, string):
        if not string:
            return
        try:
            self.clip.remove(string)
        except ValueError:
            pass
        if len(self.clip) >= self.maxsave:
            self.clip.pop(0)
        self.clip.append(string)

    def paste(self):
        if not self.clip:
            return
        pastetext = self.clip[-1]
        self.cmdline.insert(pastetext)
        self.finish()

    def draw(self):
        super(self.__class__, self).draw()
        self.textbox.draw()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        elif key == "SPC":
            self.textbox.insert(" ")
        elif util.mbslen(key) == 1:
            self.textbox.insert(key)
        else:
            self.finish()
            self.cmdline.input(key)

    def start(self):
        if not self.clip:
            return
        text = self.textbox.text
        entries = [Entry(item) for item in self.clip if text in item]
        entries.reverse()
        self.cmdline.history.hide()
        self.show(entries)
        self.textbox.panel.show()

    def finish(self):
        self.hide()
        self.textbox.hide()
        self.cmdline.history.start()

class Output(ListBox):
    def __init__(self, cmdline):
        ListBox.__init__(self)
        self.title = "output"
        self.cmdline = cmdline

    def edit(self):
        grepoutputs = self.cursor_entry().text.split(":")
        fname = grepoutputs[0]
        lnum = grepoutputs[1]
        try:
            process.spawn("{0} +{1} {2}".format(Pyful.environs["EDITOR"], lnum, fname))
        except Exception as e:
            message.exception(e)

    def communicate(self, string=None):
        if self.cmdline.mode.__class__.__name__ != "Shell":
            return
        if string is None:
            string = self.cmdline.text
        cmd = util.expandmacro(string)
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
        entries = []
        for line in (out + err).splitlines():
            try:
                line = line.decode()
                line = re.sub(r"[\r]", "", line).expandtabs()
                attr = 0
            except UnicodeError:
                line = "????? - Invalid encoding"
                attr = look.colors["ErrorMessage"]
            entries.append(Entry(line, attr=attr))
        if entries:
            self.show(entries)
        else:
            self.show([Entry("No output: `{0}'".format(cmd))])

    def terminal(self):
        pass

    def finish(self):
        self.hide()
        self.cmdline.history.start()
