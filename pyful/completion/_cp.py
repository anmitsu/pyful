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

class Cp(completion.CompletionFunction):
    def __init__(self, comp):
        arguments = {
            '--archive': comp.comp_files,
            '--copy-contents': comp.comp_files,
            '--dereference': comp.comp_files,
            '--force': comp.comp_files,
            '--interactive': comp.comp_files,
            '--link': comp.comp_files,
            '--one-file-system': comp.comp_files,
            '--parents': comp.comp_files,
            '--recursive': comp.comp_files,
            '--remove-destination': comp.comp_files,
            '--strip-trailing-slashes': comp.comp_files,
            '--symbolic-link': comp.comp_files,
            '--update': comp.comp_files,
            '--verbose': comp.comp_files,
            '-H': comp.comp_files,
            '-L': comp.comp_files,
            '-P': comp.comp_files,
            '-S': [],
            '-R': comp.comp_files,
            '-b': comp.comp_files,
            '-d': comp.comp_files,
            '-p': comp.comp_files,
            '-a': comp.comp_files,
            '-f': comp.comp_files,
            '-i': comp.comp_files,
            '-l': comp.comp_files,
            '-r': comp.comp_files,
            '-s': comp.comp_files,
            '-u': comp.comp_files,
            '-v': comp.comp_files,
            '-x': comp.comp_files,
            '--backup=': ['existing', 'never', 'nil', 'none', 'numbered', 'off', 'simple', 't'],
            '--help': comp.comp_files,
            '--no-preserve=': ['all', 'links', 'mode', 'ownership', 'timestamps'],
            '--preserve=': ['all', 'links', 'mode', 'ownership', 'timestamps'],
            '--reply=': ['no', 'query', 'yes'],
            '--sparse=': ['always', 'auto', 'never'],
            '--suffix': [],
            '--target-directory=': comp.comp_dirs,
            '--version': comp.comp_files,
            }
        completion.CompletionFunction.__init__(self, comp, arguments)

    def default(self):
        return self.comp.comp_files()

completion.register("cp", Cp)
