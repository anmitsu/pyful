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

class Sudo(completion.CompletionFunction):
    def __init__(self, comp):
        arguments = {
            "-E": comp.comp_programs,
            "-H": comp.comp_programs,
            "-K": comp.comp_programs,
            "-L": comp.comp_programs,
            "-P": comp.comp_programs,
            "-S": comp.comp_programs,
            "-V": comp.comp_programs,
            "-a": [],
            "-b": comp.comp_programs,
            "-c": [],
            "-h": comp.comp_programs,
            "-i": comp.comp_programs,
            "-k": comp.comp_programs,
            "-l": comp.comp_programs,
            "-p": [],
            "-r": [],
            "-s": comp.comp_programs,
            "-v": comp.comp_programs,
            }
        completion.CompletionFunction.__init__(self, comp, arguments)

    def default(self):
        return self.comp.comp_programs()+self.comp.comp_files()

    def comp_other_prgs(self):
        for arg in reversed(self.comp.parser.current_cmdline.split()):
            if arg != "sudo" and arg in completion.compfunctions:
                return completion.compfunctions[arg](self.comp).complete()

    def complete(self):
        candidate = self.comp_other_prgs()
        if candidate:
            return candidate

        if self.comp.parser.part[1].startswith("-"):
            return self.options()

        value = self.arguments.get(self.comp.parser.current_option, self.default)
        if hasattr(value, "__call__"):
            return value()
        else:
            return value

completion.register("sudo", Sudo)
