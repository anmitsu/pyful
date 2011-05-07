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
from pyful.completion import Argument

def _sudo_arguments(f): return (
    ("-E", "", f.comp_programs),
    ("-H", "", f.comp_programs),
    ("-K", "", f.comp_programs),
    ("-L", "", f.comp_programs),
    ("-P", "", f.comp_programs),
    ("-S", "", f.comp_programs),
    ("-V", "", f.comp_programs),
    ("-a", "", []),
    ("-b", "", f.comp_programs),
    ("-c", "", []),
    ("-h", "", f.comp_programs),
    ("-i", "", f.comp_programs),
    ("-k", "", f.comp_programs),
    ("-l", "", f.comp_programs),
    ("-p", "", []),
    ("-r", "", []),
    ("-s", "", f.comp_programs),
    ("-u", "", f.comp_username),
    ("-v", "", f.comp_programs),
    )

class Sudo(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*items) for items in _sudo_arguments(self)]

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
        candidates = self.comp_other_prgs()
        if candidates:
            return candidates

        if self.parser.part[1].startswith("-"):
            return self.options()

        current = self.parser.part[1]
        value = None
        for arg in self.arguments:
            if self.parser.current_option in arg.names:
                value = arg.callback
                break
        if value is None:
            value = self.default
        if hasattr(value, "__call__"):
            return value()
        else:
            return value

completion.register("sudo", Sudo)
