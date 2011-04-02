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

from pyful import ui
from pyful import util

compfunctions = {}

def register(name, cls):
    compfunctions[name] = cls

def _extendcompfunctions():
    libdir = os.path.dirname(os.path.abspath(__file__))
    try:
        __all__.extend(set(os.path.splitext(f)[0] for f in os.listdir(libdir)))
    except OSError:
        return
    __all__.remove("__init__")
    __all__.sort()
_extendcompfunctions()

class Completion(ui.InfoBox):
    programs = []

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "Completion")
        self.cmdline = cmdline
        self.parser = None
        self.loadprograms()

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
        maxlen = max(util.termwidth(item.string) for item in self.info)
        y, x = self.stdscr.getmaxyx()
        maxrow = x // (maxlen+2)
        if maxrow:
            return maxrow
        else:
            return 1

    def insert(self, string=None):
        if string is None:
            string = self.cursor_item().string
        if self.cmdline.mode.__class__.__name__ == "Shell" and \
                not self.parser.now_in_quote():
            string = util.string_to_safe(string)

        self.cmdline.setstring(self.parser.part[0] + string + self.parser.part[2])
        self.cmdline.cursor = util.mbslen(self.parser.part[0]+string)
        self.finish()

    def start(self):
        self.parser = Parser(self.cmdline.string, self.cmdline.cursor)
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
            info = [ui.InfoBoxContext(c, histr=self.parser.part[1]) for c in candidates]
            self.show(info)
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
            files = os.listdir(dpath)
        except OSError:
            return []
        def func(f):
            if os.path.isdir(os.path.join(dpath, f)):
                return f + os.sep
            else:
                return f
        return sorted([func(f) for f in files if f.startswith(bname)])

    def comp_dirs(self):
        bname, dpath = self._update_completion_path()
        try:
            files = os.listdir(dpath)
        except OSError:
            return []
        return sorted([f+os.sep for f in files if f.startswith(bname) and
                       os.path.isdir(os.path.join(dpath, f))])

    def comp_username(self):
        return sorted([usrname for usrname in [p[0] for p in pwd.getpwall()]
                       if usrname.startswith(self.parser.part[1])])

    def comp_groupname(self):
        return sorted([grpname for grpname in [g[0] for g in grp.getgrall()]
                       if grpname.startswith(self.parser.part[1])])

    def comp_programs(self):
        return sorted([item for item in Completion.programs
                       if item.startswith(self.parser.part[1])])

    def comp_pyful_commands(self):
        from pyful.command import commands
        return sorted([cmd for cmd in commands.keys()
                       if cmd.startswith(self.parser.part[1])])

    def comp_python_builtin_functions(self):
        return sorted([func for func in __builtins__.keys()
                       if func.startswith(self.parser.part[1])])

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
