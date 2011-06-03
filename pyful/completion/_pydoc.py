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

import keyword
import os
import sys

from pyful import completion
from pyful.completion import Argument

def _pydoc_arguments(f): return (
    ("-g"  , "-- gui", f.modules_and_keywords),
    ("-k"  , "-- keyword", f.modules_and_keywords),
    ("-p"  , "-- port", []),
    ("-w"  , "-- write out HTML", f.comp_files),
    )

class Pydoc(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _pydoc_arguments(self)]

    def default(self):
        return self.modules_and_keywords()

    def modules_and_keywords(self):
        modules = []
        for path in sys.path:
            try:
                entries = os.listdir(path)
            except OSError:
                continue
            for module in entries:
                name, ext = os.path.splitext(module)
                if ext in (".py", ".pyc", "pyo") or \
                        (os.path.isdir(os.path.join(path, module)) and not ext):
                    modules.append(name)
        modules = list(set(modules))
        modules.sort()
        return modules + keyword.kwlist

completion.register("pydoc", Pydoc)
