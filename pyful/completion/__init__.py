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

import glob
import grp
import os
import pwd
import re
import sys

from pyful import ui
from pyful import util

optionsdict = {}

class Completion(ui.InfoBox):
    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "Completion")
        self.cmdline = cmdline
        self.parser = None
        self.programs = []
        self.loadprograms()
        self.loadoptions()

    def input(self, meta, key):
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
        else:
            self.finish()
            self.cmdline.input(meta, key)

    def loadoptions(self):
        readdir = os.path.dirname(util.abspath(__file__))
        for f in os.listdir(readdir):
            path = os.path.join(readdir, f)
            if util.extname(path) == ".py" and f.startswith('_') and f != "__init__.py":
                with open(path, 'r') as opt:
                    exec(opt.read(), locals())

    def loadprograms(self):
        osname = sys.platform
        self.programs[:] = []
        for path in os.environ['PATH'].split(os.pathsep):
            if os.path.exists(path):
                for name in os.listdir(path):
                    if osname == 'cygwin':
                        ext = util.extname(name)
                        if ext == '.exe':
                            self.programs.append(name.replace(ext, ""))
                    else:
                        self.programs.append(name)
        self.programs = sorted(self.programs)

    def _get_maxrow(self):
        maxlen = max(util.termwidth(item.string) for item in self.info)
        y, x = self.stdscr.getmaxyx()
        maxrow = x // (maxlen+2)
        if maxrow:
            return maxrow
        else:
            return 1

    def _insert_string_to_safe(self, string):
        if self.cmdline.mode.__class__.__name__ != "Shell":
            return string
        psquote = pdquote = False
        for c in self.parser.part[0]:
            if c == "'":
                if not pdquote:
                    psquote = not psquote
            elif c == '"':
                if not psquote:
                    pdquote = not pdquote
        fsquote = fdquote = False
        for c in self.parser.part[2]:
            if c == "'":
                if not fdquote and not pdquote:
                    fsquote = not fsquote
            elif c == '"':
                if not fsquote and not psquote:
                    fdquote = not fdquote
        if (psquote and fsquote) or (pdquote and fdquote):
            return string
        else:
            return util.string_to_safe(string)

    def insert(self, string=None):
        if string is None:
            string = self.cursor_item().string
        string = self._insert_string_to_safe(string)
        self.cmdline.string = self.parser.part[0] + string + self.parser.part[2]
        self.cmdline.cursor = util.mbslen(self.parser.part[0]+string)
        self.finish()

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
        if self.cmdline.mode.__class__.__name__ == "Shell":
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
        return sorted([item for item in self.programs
                       if item.startswith(self.parser.part[1])])

    def comp_pyful_commands(self):
        from pyful.command import commands
        return sorted([cmd for cmd in commands.keys()
                       if cmd.startswith(self.parser.part[1])])

    def comp_python_builtin_functions(self):
        return sorted([func for func in __builtins__.keys()
                       if func.startswith(self.parser.part[1])])

    def comp_program_options(self):
        if self.parser.prgname in optionsdict:
            option = optionsdict[self.parser.prgname](self)
            return option.complete()
        elif self.parser.prgname == "":
            return self.comp_programs()
        else:
            return self.comp_files()

    def start(self):
        self.parser = Parser(self.cmdline.string, self.cmdline.cursor)
        if self.cmdline.mode.__class__.__name__ == "Shell":
            self.parser.parse()
        else:
            self.parser.parse_nonshell()

        candidate = self.cmdline.mode.complete(self)

        if not isinstance(candidate, list) or len(candidate) == 0:
            return
        if len(candidate) == 1:
            if candidate[0] == self.parser.part[1]:
                return
            self.insert(candidate[0])
            self.hide()
        else:
            self.cmdline.history.hide()
            common = os.path.commonprefix(candidate)
            if common:
                self.insert(common)
                self.parser.part[1] = common
            info = [ui.InfoBoxContext(c, histr=self.parser.part[1]) for c in candidate]
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
        for c in re.split(r"((?<!\\)[\s;|,=\"'])", string[:self.pos]):
            ns += c
            if re.match(r"(?<!\\)[\s;|,=\"']", c):
                ps += ns
                ns = ""
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
                            if arg.startswith('--')]
        self.options = [arg for arg in
                        re.split("[\s=;|]", self.current_cmdline)
                        if arg.startswith('-')]
        self.prgname = re.split("([\s])", self.current_cmdline.strip())[0]

class CompletionFunction(object):
    def __init__(self, comp, arguments):
        self.comp = comp
        self.arguments = arguments

    def default(self):
        return self.options()

    def options(self):
        return sorted(
            [opt for opt in self.arguments.keys()
             if opt.startswith(self.comp.parser.part[1])
             and not opt in self.comp.parser.options])

    def complete(self):
        if self.comp.parser.part[1].startswith("-"):
            return self.options()

        value = self.arguments.get(self.comp.parser.current_option, self.default)
        if hasattr(value, "__call__"):
            return value()
        else:
            return value
