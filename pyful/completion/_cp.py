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
