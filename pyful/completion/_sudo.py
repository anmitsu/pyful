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

class Sudo(object):
    def __init__(self, comp):
        self.comp = comp
        self.arguments = {
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
        return (self.comp.comp_programs()+self.comp.comp_files())

    def options(self):
        ret = [opt for opt in self.arguments.keys()
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
        value = self.arguments.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

from pyful.completion import optionsdict
optionsdict.update({"sudo": Sudo})

