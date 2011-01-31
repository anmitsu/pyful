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

from pyful.completion import CompletionFunction
from pyful.completion import optionsdict

class Make(CompletionFunction):
    def __init__(self, comp):
        arguments = {
            '--directory=': lambda: self.comp.comp_dirs(),
            '--debug': [],
            '--environment-overrides': [],
            '--file=': lambda: self.comp.comp_files(),
            '--makefile=': lambda: self.comp.comp_files(),
            '--help': [],
            '--ignore-errors': [],
            '--include-dir=': lambda: self.comp.comp_dirs(),
            '--jobs=': [],
            '--keep-going': [],
            '--load-average=': [],
            '--max-load=': [],
            '--just-print': [],
            '--dry-run': [],
            '--recon': [],
            '--old-file=': lambda: self.comp.comp_files(),
            '--assume-old=': lambda: self.comp.comp_files(),
            '--print-data-base': [],
            '--question': [],
            '--no-builtin-rules': [],
            '--silent': [],
            '--quiet': [],
            '--no-keep-going': [],
            '--stop': [],
            '--touch': [],
            '--version': [],
            '--print-directory': [],
            '--no-print-directory': [],
            '--what-if=': lambda: self.comp.comp_files(),
            '--new-file=': lambda: self.comp.comp_files(),
            '--assume-new=': lambda: self.comp.comp_files(),
            '--warn-undefined-variables': [],

            '-b': [],
            '-m': [],
            '-C': lambda: self.comp.comp_dirs(),
            '-d': [],
            '-e': [],
            '-f': lambda: self.comp.comp_files(),
            '-h': [],
            '-i': [],
            '-I': lambda: self.comp.comp_dirs(),
            '-j': [],
            '-k': [],
            '-l': [],
            '-n': [],
            '-o': lambda: self.comp.comp_files(),
            '-p': [],
            '-q': [],
            '-r': [],
            '-s': [],
            '-S': [],
            '-t': [],
            '-v': [],
            '-w': [],
            '-W': lambda: self.comp.comp_files(),
            }
        CompletionFunction.__init__(self, comp, arguments)

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

optionsdict.update({"make": Make})
