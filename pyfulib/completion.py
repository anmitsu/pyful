# completion.py - completion management of cmdline.
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
import glob
import subprocess
import pwd
import grp

from pyfulib.core import Pyful
from pyfulib import util
from pyfulib import ui

pyful = Pyful()

class Completion(ui.InfoBox):
    program_options = {}

    def __init__(self, cmdline):
        ui.InfoBox.__init__(self, "completion")
        self.cmdline = cmdline
        self.maxrow = 1
        self.parser = None
        self.programs = []
        self.loadprograms()

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

    def loadprograms(self):
        self.programs[:] = []
        for path in os.environ['PATH'].split(os.pathsep):
            if os.path.exists(path):
                for name in os.listdir(path):
                    self.programs.append(name)
        self.programs = sorted(self.programs)

    def get_maxrow(self):
        length = 1
        for item in self.info:
            width = util.termwidth(item)
            if width > length:
                length = width
        maxrow = pyful.stdscr.maxx // (length+4)
        if maxrow:
            return maxrow
        else:
            return 1

    def insert(self, string=None):
        if string is None:
            string = self.cursor_item()

        from pyfulib.mode import Shell
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
        from pyfulib.command import commands
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
        string = util.unistr(string)
        for c in string[:pos]:
            ns += c
            if re.search("[\s;|,=\"']", c):
                ps += ns
                ns = ""
        fs = string[pos:]
        return (ps, ns, fs)


class Sudo(object):
    _dict = None

    def __init__(self, comp):
        self.comp = comp
        self.__class__._dict = {
            "-E": self.comp.comp_programs,
            "-H": self.comp.comp_programs,
            "-K": self.comp.comp_programs,
            "-L": self.comp.comp_programs,
            "-P": self.comp.comp_programs,
            "-S": self.comp.comp_programs,
            "-V": self.comp.comp_programs,
            "-a": [],
            "-b": self.comp.comp_programs,
            "-c": [],
            "-h": self.comp.comp_programs,
            "-i": self.comp.comp_programs,
            "-k": self.comp.comp_programs,
            "-l": self.comp.comp_programs,
            "-p": [],
            "-r": [],
            "-s": self.comp.comp_programs,
            "-v": self.comp.comp_programs,
            }

    def default(self):
        return self.comp.comp_programs()

    def options(self):
        ret = [opt for opt in self._dict.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def comp_other_prgs(self):
        optlist = list(optionsdict.keys())
        for arg in reversed(self.comp.parser.current_cmdline.split()):
            if arg != "sudo" and arg in optlist:
                return optionsdict[arg](self.comp).complete()
        return

    def complete(self):
        if self.comp.parser.nowstr.startswith("-"):
            return self.options()

        candidate = self.comp_other_prgs()
        if candidate:
            return candidate

        opt = self.comp.parser.current_option
        value = self._dict.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

class AptGet(object):
    _dict = None

    def __init__(self, comp):
        self.comp = comp
        self.__class__._dict = {
            'autoclean'      : [],
            'autoremove'     : self.comp_dpkglist,
            'build-dep'      : self.comp_pkgnames,
            'check'          : [],
            'clean'          : [],
            'dist-upgrade'   : [],
            'dselect-upgrade': [],
            'install'        : self.comp_pkgnames,
            'purge'          : self.comp_dpkglist,
            'remove'         : self.comp_dpkglist,
            'source'         : self.comp_pkgnames,
            'update'         : [],
            'upgrade'        : [],
            'help'           : [],
            }

    def options(self):
        ret = [opt for opt in self._dict.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def default(self):
        return self.options()

    def comp_pkgnames(self):
        (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        li = out.split("\n")
        ret = [item for item in li if item.startswith(self.comp.parser.nowstr)]
        return ret

    def comp_dpkglist(self):
        (out, err) = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        pkgs = []
        for i, line in enumerate(out.split("\n")):
            if i > 4:
                li = line.split()
                if len(li) > 2 and li[1].startswith(self.comp.parser.nowstr):
                    pkgs.append(li[1])
        return pkgs

    def complete(self):
        opt = self.comp.parser.current_option
        value = self._dict.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

class AptCache(object):
    _dict = None

    def __init__(self, comp):
        self.comp = comp
        self.__class__._dict = {
            'add'      : [],
            'depends'  : self.comp_pkgnames,
            'dotty'    : self.comp_pkgnames,
            'dump'     : [],
            'dumpavail': [],
            'gencaches': [],
            'help'     : [],
            'madison'  : self.comp_pkgnames,
            'pkgnames' : [],
            'policy'   : self.comp_pkgnames,
            'rdepends' : self.comp_pkgnames,
            'search'   : [],
            'show'     : self.comp_pkgnames,
            'showpkg'  : self.comp_pkgnames,
            'showsrc'  : self.comp_pkgnames,
            'stats'    : [],
            'unmet'    : [],
            'xvcg'     : self.comp_pkgnames,
            }

    def default(self):
        return self.options()

    def options(self):
        ret = [opt for opt in self._dict.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def comp_pkgnames(self):
        (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        li = out.split("\n")
        ret = [item for item in li if item.startswith(self.comp.parser.nowstr)]
        return ret

    def complete(self):
        opt = self.comp.parser.current_option
        value = self._dict.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

class Cp(object):
    _dict = None

    def __init__(self, comp):
        self.comp = comp
        self.__class__._dict = {
            '--archive'                : self.comp.comp_files,
            '--copy-contents'          : self.comp.comp_files,
            '--dereference'            : self.comp.comp_files,
            '--force'                  : self.comp.comp_files,
            '--interactive'            : self.comp.comp_files,
            '--link'                   : self.comp.comp_files,
            '--one-file-system'        : self.comp.comp_files,
            '--parents'                : self.comp.comp_files,
            '--recursive'              : self.comp.comp_files,
            '--remove-destination'     : self.comp.comp_files,
            '--strip-trailing-slashes' : self.comp.comp_files,
            '--symbolic-link'          : self.comp.comp_files,
            '--update'                 : self.comp.comp_files,
            '--verbose'                : self.comp.comp_files,
            '-H' : self.comp.comp_files,
            '-L' : self.comp.comp_files,
            '-P' : self.comp.comp_files,
            '-S' : [],
            '-R' : self.comp.comp_files,
            '-b' : self.comp.comp_files,
            '-d' : self.comp.comp_files,
            '-p' : self.comp.comp_files,
            '-a' : self.comp.comp_files,
            '-f' : self.comp.comp_files,
            '-i' : self.comp.comp_files,
            '-l' : self.comp.comp_files,
            '-r' : self.comp.comp_files,
            '-s' : self.comp.comp_files,
            '-u' : self.comp.comp_files,
            '-v' : self.comp.comp_files,
            '-x' : self.comp.comp_files,
            '--backup='          : ['existing', 'never', 'nil', 'none', 'numbered', 'off', 'simple', 't'],
            '--help'             : self.comp.comp_files,
            '--no-preserve='     : ['all', 'links', 'mode', 'ownership', 'timestamps'],
            '--preserve='        : ['all', 'links', 'mode', 'ownership', 'timestamps'],
            '--reply='           : ['no', 'query', 'yes'],
            '--sparse='          : ['always', 'auto', 'never'],
            '--suffix'           : [],
            '--target-directory=': self.comp.comp_dirs,
            '--version'          : self.comp.comp_files,
            }

    def default(self):
        return self.comp.comp_files()

    def options(self):
        ret = [opt for opt in self._dict.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def complete(self):
        if self.comp.parser.nowstr.startswith("-"):
            return self.options()

        opt = self.comp.parser.current_option
        value = self._dict.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

class Make(object):
    _dict = None

    def __init__(self, comp):
        self.comp = comp
        self.__class__._dict = {
            '--directory='               : lambda: self.comp.comp_dirs(),
            '--debug'                    : [],
            '--environment-overrides'    : [],
            '--file='                    : lambda: self.comp.comp_files(),
            '--makefile='                : lambda: self.comp.comp_files(),
            '--help'                     : [],
            '--ignore-errors'            : [],
            '--include-dir='             : lambda: self.comp.comp_dirs(),
            '--jobs='                    : [],
            '--keep-going'               : [],
            '--load-average='            : [],
            '--max-load='                : [],
            '--just-print'               : [],
            '--dry-run'                  : [],
            '--recon'                    : [],
            '--old-file='                : lambda: self.comp.comp_files(),
            '--assume-old='              : lambda: self.comp.comp_files(),
            '--print-data-base'          : [],
            '--question'                 : [],
            '--no-builtin-rules'         : [],
            '--silent'                   : [],
            '--quiet'                    : [],
            '--no-keep-going'            : [],
            '--stop'                     : [],
            '--touch'                    : [],
            '--version'                  : [],
            '--print-directory'          : [],
            '--no-print-directory'       : [],
            '--what-if='                 : lambda: self.comp.comp_files(),
            '--new-file='                : lambda: self.comp.comp_files(),
            '--assume-new='              : lambda: self.comp.comp_files(),
            '--warn-undefined-variables' : [],

            '-b' : [],
            '-m' : [],
            '-C' : lambda: self.comp.comp_dirs(),
            '-d' : [],
            '-e' : [],
            '-f' : lambda: self.comp.comp_files(),
            '-h' : [],
            '-i' : [],
            '-I' : lambda: self.comp.comp_dirs(),
            '-j' : [],
            '-k' : [],
            '-l' : [],
            '-n' : [],
            '-o' : lambda: self.comp.comp_files(),
            '-p' : [],
            '-q' : [],
            '-r' : [],
            '-s' : [],
            '-S' : [],
            '-t' : [],
            '-v' : [],
            '-w' : [],
            '-W' : lambda: self.comp.comp_files(),
            }

    def default(self):
        fname = ""
        if os.path.exists("GNUmakefile"):
            fname = "GNUmakefile"
        elif os.path.exists("makefile"):
            fname = "makefile"
        elif os.path.exists("Makefile"):
            fname = "Makefile"
        if not fname:
            return []

        command = []
        with open(fname) as f:
            for line in f:
                tmp = line.split(":")
                if len(tmp) == 2 and "$" not in tmp[0] and "\t" not in tmp[0] and not tmp[0].startswith("#"):
                    if tmp[0].startswith(self.comp.parser.nowstr):
                        command.append(tmp[0])
        return sorted(command)

    def options(self):
        ret = [opt for opt in self._dict.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def complete(self):
        if self.comp.parser.nowstr.startswith("-"):
            return self.options()

        opt = self.comp.parser.current_option
        value = self._dict.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

optionsdict = {
    "apt-get": AptGet,
    "apt-cache": AptCache,
    "cp": Cp,
    "make": Make,
    "sudo": Sudo,
    }

