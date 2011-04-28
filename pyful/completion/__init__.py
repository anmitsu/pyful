# completion.py - completion management of cmdline.
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

__all__ = []

import grp
import os
import pwd
import re
import sys

from pyful import util

from pyful.widget.listbox import ListBox, Entry

compfunctions = {}

def register(name, cls):
    compfunctions[name] = cls

def import_completion_functions(path=None):
    if path is None:
        path = os.path.dirname(os.path.abspath(__file__))
    try:
        modules = list(set(os.path.splitext(f)[0] for f in os.listdir(path)))
    except OSError:
        return
    try:
        modules.remove("__init__")
    except ValueError:
        pass
    __all__.extend(modules)
    __import__("pyful.completion", {}, {}, modules)

class Completion(ListBox):
    programs = []

    def __init__(self, cmdline):
        ListBox.__init__(self, "Completion")
        self.cmdline = cmdline
        self.parser = None
        self.loadprograms()
        import_completion_functions()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        else:
            self.finish()
            self.cmdline.input(key)

    def loadprograms(self):
        osname = sys.platform
        self.__class__.programs[:] = []
        for path in os.getenv("PATH").split(os.pathsep):
            try:
                files = os.listdir(path)
            except OSError:
                continue
            for f in files:
                if osname == "cygwin":
                    ext = util.extname(f)
                    if ext != ".exe":
                        continue
                    f = f.replace(ext, "")
                self.programs.append(f)
        self.programs.sort()

    def _get_maxrow(self):
        maxlen = max(util.termwidth(entry.text) for entry in self.list)
        y, x = self.stdscr.getmaxyx()
        maxrow = x // (maxlen+2)
        if maxrow:
            return maxrow
        else:
            return 1

    def insert(self, text=None):
        if text is None:
            text = self.cursor_entry().text
        if self.cmdline.mode.__class__.__name__ == "Shell" and \
                not self.parser.now_in_quote():
            text = util.string_to_safe(text)

        self.cmdline.settext(self.parser.part[0] + text + self.parser.part[2])
        self.cmdline.cursor = util.mbslen(self.parser.part[0]+text)
        self.finish()

    def start(self):
        self.parser = Parser(self.cmdline.text, self.cmdline.cursor)
        CompletionFunction.parser = self.parser
        if self.cmdline.mode.__class__.__name__ == "Shell":
            self.parser.parse()
            compfunc = compfunctions.get(self.parser.prgname, ShellCompletionFunction)()
        else:
            self.parser.parse_nonshell()
            compfunc = CompletionFunction()

        candidates = self.cmdline.mode.complete(compfunc)

        if not isinstance(candidates, list) or len(candidates) == 0:
            return
        if len(candidates) == 1:
            if candidates[0] == self.parser.part[1]:
                return
            self.insert(candidates[0])
            self.hide()
        else:
            self.cmdline.history.hide()
            common = os.path.commonprefix(candidates)
            if common:
                self.insert(common)
                self.parser.part[1] = common
            entries = [Entry(c, histr=self.parser.part[1]) for c in candidates]
            self.show(entries)
            self.maxrow = self._get_maxrow()

    def finish(self):
        self.hide()
        self.cmdline.history.start()

class Parser(object):
    def __init__(self, string, pos):
        self.string = string
        self.pos = pos
        self.current_cmdline = []
        self.current_option = ""
        self.options = []
        self.longoptions = []
        self.prgname = ""

    def parse_nonshell(self):
        string = util.U(self.string)
        self.part = ["", string[:self.pos], string[self.pos:]]
        self.current_cmdline = self.string

    def parse(self):
        ps = ns = fs = ""
        string = util.U(self.string)
        sq = dq = 0
        for c in re.split(r"((?<!\\)[\s;|,=\"'])", string[:self.pos]):
            ns += c
            if re.match(r"(?<!\\)[\s;|,=\"']", c):
                if not (dq % 2 or sq % 2):
                    ps += ns
                    ns = ""
                if c == "'":
                    if dq % 2 == 0:
                        sq += 1
                elif c == '"':
                    if sq % 2 == 0:
                        dq += 1
        fs = string[self.pos:]
        ns = util.string_to_norm(ns)
        self.part = [ps, ns, fs]

        pseps = re.split("[;|]", self.part[0])
        fseps = re.split("[;|]", self.part[2])
        if len(fseps) > 1:
            self.current_cmdline = pseps[-1] + fseps[0]
        else:
            self.current_cmdline = pseps[-1]

        self.current_option = ""
        if len(self.current_cmdline.split()):
            self.current_option = self.current_cmdline.split()[-1]
        self.longoptions = [arg for arg in
                            re.split("[\s=;|]", self.current_cmdline)
                            if arg.startswith("--")]
        self.options = [arg for arg in
                        re.split("[\s=;|]", self.current_cmdline)
                        if arg.startswith("-")]
        self.prgname = re.split("([\s])", self.current_cmdline.strip())[0]

    def now_in_quote(self):
        psq = pdq = fsq = fdq = False
        for c in re.split(r"((?<!\\)[\"'])", self.part[0]):
            if c == "'":
                if not pdq:
                    psq = not psq
            elif c == '"':
                if not psq:
                    pdq = not pdq
        for c in re.split(r"((?<!\\)[\"'])", self.part[2]):
            if c == "'":
                if not fdq and not pdq:
                    fsq = not fsq
            elif c == '"':
                if not fsq and not psq:
                    fdq = not fdq
        return (psq and fsq) or (pdq and fdq)

    def match_current_part(self, text):
        return text.startswith(self.part[1])

class CompletionFunction(object):
    parser = None

    def _update_completion_path(self):
        def _dirname(path_):
            if path_.endswith(os.sep):
                return path_
            else:
                dname = os.path.dirname(path_)
                if dname.endswith(os.sep) or not dname:
                    return dname
                else:
                    return dname + os.sep
        path = self.parser.part[1]
        if issubclass(self.__class__, ShellCompletionFunction) and \
                not self.parser.now_in_quote():
            self.parser.part[0] += _dirname(util.string_to_safe(path))
        else:
            self.parser.part[0] += _dirname(path)
        bname = os.path.basename(path)
        dpath = os.path.expanduser(util.abspath(os.path.dirname(path)))
        return (bname, dpath)

    def comp_files(self):
        bname, dpath = self._update_completion_path()
        try:
            entries = os.listdir(dpath)
        except OSError:
            return []
        files = []
        for fname in entries:
            if fname.startswith(bname):
                if os.path.isdir(os.path.join(dpath, fname)):
                    files.append(fname+os.sep)
                else:
                    files.append(fname)
        files.sort()
        return files

    def comp_dirs(self):
        bname, dpath = self._update_completion_path()
        try:
            entries = os.listdir(dpath)
        except OSError:
            return []
        dirs = []
        for fname in entries:
            if fname.startswith(bname):
                if os.path.isdir(os.path.join(dpath, fname)):
                    dirs.append(fname+os.sep)
        dirs.sort()
        return dirs

    def comp_username(self):
        usrnames = zip(*pwd.getpwall())[0]
        candidates = []
        for name in usrnames:
            if self.parser.match_current_part(name):
                candidates.append(name)
        candidates.sort()
        return candidates

    def comp_groupname(self):
        grpnames = zip(*grp.getgrall())[0]
        candidates = []
        for name in grpnames:
            if self.parser.match_current_part(name):
                candidates.append(name)
        candidates.sort()
        return candidates

    def comp_programs(self):
        candidates = []
        for program in Completion.programs:
            if self.parser.match_current_part(program):
                candidates.append(program)
        candidates.sort()
        return candidates

    def comp_pyful_commands(self):
        from pyful.command import commands
        candidates = []
        for cmdname in commands:
            if self.parser.match_current_part(cmdname):
                candidates.append(cmdname)
        candidates.sort()
        return candidates

    def comp_python_builtin_functions(self):
        candidates = []
        for func in __builtins__.keys():
            if self.parser.match_current_part(func):
                candidates.append(func)
        candidates.sort()
        return candidates

class ShellCompletionFunction(CompletionFunction):
    arguments = None

    def default(self):
        return self.options()

    def options(self):
        return sorted(
            [opt for opt in self.arguments.keys()
             if opt.startswith(self.parser.part[1])
             and not opt in self.parser.options])

    def complete(self):
        if self.arguments:
            if self.parser.part[1].startswith("-"):
                return self.options()
            value = self.arguments.get(self.parser.current_option, self.default)
            if hasattr(value, "__call__"):
                return value()
            else:
                return value
        else:
            if self.parser.prgname == "":
                return self.comp_programs()
            else:
                return self.comp_files()
