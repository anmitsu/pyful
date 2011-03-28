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

from pyful import completion

class Sudo(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = {
            "-E": self.comp_programs,
            "-H": self.comp_programs,
            "-K": self.comp_programs,
            "-L": self.comp_programs,
            "-P": self.comp_programs,
            "-S": self.comp_programs,
            "-V": self.comp_programs,
            "-a": [],
            "-b": self.comp_programs,
            "-c": [],
            "-h": self.comp_programs,
            "-i": self.comp_programs,
            "-k": self.comp_programs,
            "-l": self.comp_programs,
            "-p": [],
            "-r": [],
            "-s": self.comp_programs,
            "-v": self.comp_programs,
            }

    def default(self):
        progs = self.comp_programs()
        if progs:
            return progs
        return self.comp_files()

    def comp_other_prgs(self):
        for arg in reversed(self.parser.current_cmdline.split()):
            if arg != "sudo" and arg in completion.compfunctions:
                return completion.compfunctions[arg]().complete()

    def complete(self):
        candidate = self.comp_other_prgs()
        if candidate:
            return candidate

        if self.parser.part[1].startswith("-"):
            return self.options()

        value = self.arguments.get(self.parser.current_option, self.default)
        if hasattr(value, "__call__"):
            return value()
        else:
            return value

completion.register("sudo", Sudo)
