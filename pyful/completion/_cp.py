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

class Cp(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = {
            "--archive": self.comp_files,
            "--copy-contents": self.comp_files,
            "--dereference": self.comp_files,
            "--force": self.comp_files,
            "--interactive": self.comp_files,
            "--link": self.comp_files,
            "--one-file-system": self.comp_files,
            "--parents": self.comp_files,
            "--recursive": self.comp_files,
            "--remove-destination": self.comp_files,
            "--strip-trailing-slashes": self.comp_files,
            "--symbolic-link": self.comp_files,
            "--update": self.comp_files,
            "--verbose": self.comp_files,
            "-H": self.comp_files,
            "-L": self.comp_files,
            "-P": self.comp_files,
            "-S": [],
            "-R": self.comp_files,
            "-b": self.comp_files,
            "-d": self.comp_files,
            "-p": self.comp_files,
            "-a": self.comp_files,
            "-f": self.comp_files,
            "-i": self.comp_files,
            "-l": self.comp_files,
            "-r": self.comp_files,
            "-s": self.comp_files,
            "-u": self.comp_files,
            "-v": self.comp_files,
            "-x": self.comp_files,
            "--backup=": ["existing", "never", "nil", "none", "numbered", "off", "simple", "t"],
            "--help": self.comp_files,
            "--no-preserve=": ["all", "links", "mode", "ownership", "timestamps"],
            "--preserve=": ["all", "links", "mode", "ownership", "timestamps"],
            "--reply=": ["no", "query", "yes"],
            "--sparse=": ["always", "auto", "never"],
            "--suffix": [],
            "--target-directory=": self.comp_dirs,
            "--version": self.comp_files,
            }

    def default(self):
        return self.comp_files()

completion.register("cp", Cp)
