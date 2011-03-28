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

import os

from pyful import completion

class Make(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = {
            "--directory=": self.comp_dirs,
            "--debug": [],
            "--environment-overrides": [],
            "--file=": self.comp_files,
            "--makefile=": self.comp_files,
            "--help": [],
            "--ignore-errors": [],
            "--include-dir=": self.comp_dirs,
            "--jobs=": [],
            "--keep-going": [],
            "--load-average=": [],
            "--max-load=": [],
            "--just-print": [],
            "--dry-run": [],
            "--recon": [],
            "--old-file=": self.comp_files,
            "--assume-old=": self.comp_files,
            "--print-data-base": [],
            "--question": [],
            "--no-builtin-rules": [],
            "--silent": [],
            "--quiet": [],
            "--no-keep-going": [],
            "--stop": [],
            "--touch": [],
            "--version": [],
            "--print-directory": [],
            "--no-print-directory": [],
            "--what-if=": self.comp_files,
            "--new-file=": self.comp_files,
            "--assume-new=": self.comp_files,
            "--warn-undefined-variables": [],
            "-b": [],
            "-m": [],
            "-C": self.comp_dirs,
            "-d": [],
            "-e": [],
            "-f": self.comp_files,
            "-h": [],
            "-i": [],
            "-I": self.comp_dirs,
            "-j": [],
            "-k": [],
            "-l": [],
            "-n": [],
            "-o": self.comp_files,
            "-p": [],
            "-q": [],
            "-r": [],
            "-s": [],
            "-S": [],
            "-t": [],
            "-v": [],
            "-w": [],
            "-W": self.comp_files,
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
                    if tmp[0].startswith(self.parser.part[1]):
                        command.append(tmp[0])
        return sorted(command)

completion.register("make", Make)
