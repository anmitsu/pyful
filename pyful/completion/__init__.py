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
    program_options = {}

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "Completion")
        self.cmdline = cmdline
        self.maxrow = 1
        self.parser = None
        self.programs = []
        self.loadprograms()
        self.loadoptions()

    def pagedown(self):
        self.mvcursor(self.maxrow * self.win.getmaxyx()[0] - self.maxrow*2)

    def pageup(self):
        self.mvcursor(- (self.maxrow * self.win.getmaxyx()[0] - self.maxrow*2))

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

    def get_maxrow(self):
        length = 1
        for item in self.info:
            width = util.termwidth(item)
            if width > length:
                length = width
        maxrow = ui.getcomponent("Stdscr").win.getmaxyx()[1] // (length+4)
        if maxrow:
            return maxrow
        else:
            return 1

    def insert(self, string=None):
        if string is None:
            string = self.cursor_item()

        try:
            util.U(string)
        except UnicodeError:
            return self.finish()

        from pyful.mode import Shell
        if isinstance(self.cmdline.mode, Shell):
            psquote = False
            pdquote = False
            for c in self.parser.paststr:
                if c == "'":
                    if not pdquote:
                        psquote = not psquote
                elif c == '"':
                    if not psquote:
                        pdquote = not pdquote
            fsquote = False
            fdquote = False
            for c in self.parser.futurestr:
                if c == "'":
                    if not fdquote and not pdquote:
                        fsquote = not fsquote
                elif c == '"':
                    if not fsquote and not psquote:
                        fdquote = not fdquote

            if (psquote and fsquote) or (pdquote and fdquote):
                pass
            else:
                string = util.string_to_safe(string)

        self.cmdline.string = self.parser.paststr + string + self.parser.futurestr
        self.cmdline.cursor = util.mbslen(self.parser.paststr+string)
        self.finish()

    def dirname(self, path):
        if path.endswith(os.sep):
            return path
        else:
            dirname =  util.unix_dirname(path)
            if dirname == "":
                return dirname
            elif not dirname.endswith(os.sep):
                return dirname + os.sep
            else:
                return dirname

    def comp_files(self):
        self.parser.paststr += self.dirname(self.parser.nowstr)
        path = os.path.expanduser(self.parser.nowstr)

        files = []
        for f in glob.glob(path+"*"):
            if os.path.isdir(f):
                f = util.unix_basename(f) + os.sep
            else:
                f = util.unix_basename(f)
            files.append(f)
        return sorted(files)

    def comp_dirs(self):
        self.parser.paststr += self.dirname(self.parser.nowstr)
        path = os.path.expanduser(self.parser.nowstr)

        dirs = []
        for f in glob.glob(path+"*"):
            if os.path.isdir(f):
                f = util.unix_basename(f) + os.sep
                dirs.append(f)
        return sorted(dirs)

    def comp_username(self):
        return sorted([usrname for usrname in [p[0] for p in pwd.getpwall()]
                       if usrname.startswith(self.parser.nowstr)])

    def comp_groupname(self):
        return sorted([grpname for grpname in [g[0] for g in grp.getgrall()]
                       if grpname.startswith(self.parser.nowstr)])

    def comp_programs(self):
        return sorted([item for item in self.programs
                       if item.startswith(self.parser.nowstr)])

    def comp_pyful_commands(self):
        from pyful.command import commands
        return sorted([cmd for cmd in list(commands.keys())
                       if cmd.startswith(self.parser.nowstr)])

    def comp_python_builtin_functions(self):
        return sorted([func for func in list(__builtins__.keys())
                       if func.startswith(self.parser.nowstr)])

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

        candidate = self.cmdline.mode.complete(self)

        if not isinstance(candidate, list) or len(candidate) == 0:
            return

        if len(candidate) == 1:
            if candidate[0] == self.parser.nowstr:
                return
            self.insert(candidate[0])
            self.hide()
        else:
            self.cmdline.history.hide()
            self.show(candidate, highlight=self.cmdline.string)
            self.maxrow = self.get_maxrow()

    def finish(self):
        self.hide()
        self.cmdline.history.start()

class Parser(object):
    paststr = None
    nowstr = None
    futurestr = None
    current_cmdline = None
    options = None
    prgname = None

    def __init__(self, string, pos):
        (self.paststr, self.nowstr, self.futurestr) = self.parse(string, pos)

        past_sepetes = re.split("[;|]", self.paststr)
        futures_seperates = re.split("[;|]", self.futurestr)
        if len(futures_seperates) > 1:
            self.current_cmdline = past_sepetes[-1] + futures_seperates[0]
        else:
            self.current_cmdline = past_sepetes[-1]

        # self.current_option = re.split("[\s=;|]", self.current_cmdline)[-1]
        self.current_option = ""
        if not len(self.current_cmdline.split()) == 0:
            self.current_option = self.current_cmdline.split()[-1]
        # self.current_option = ""
        # for arg in reversed(re.split("[\s=;|]", past_sepetes[-1])):
        #     if arg.startswith("-"):
        #         self.current_option = arg
        #         break

        self.options = [arg for arg in re.split("[\s=;|]", self.current_cmdline) if arg.startswith('-')]
        self.prgname = re.split("([\s])", self.current_cmdline.strip())[0]

    def parse(self, string, pos):
        ps = ""
        ns = ""
        fs = ""
        string = util.U(string)
        for c in string[:pos]:
            ns += c
            if re.search("[\s;|,=\"']", c):
                ps += ns
                ns = ""
        fs = string[pos:]
        return (ps, ns, fs)

class CompletionFunction(object):
    def __init__(self, comp, arguments):
        self.comp = comp
        self.arguments = arguments

    def default(self):
        return self.options()

    def options(self):
        ret = [opt for opt in self.arguments.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def complete(self):
        if self.comp.parser.nowstr.startswith("-"):
            return self.options()

        value = self.arguments.get(self.comp.parser.current_option, self.default)
        if hasattr(value, "__call__"):
            return value()
        else:
            return value
