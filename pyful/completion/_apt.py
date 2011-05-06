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
import subprocess

from pyful import completion
from pyful.completion import Argument

def _aptget_arguments(f): return (
    ("autoclean"      , "", []),
    ("autoremove"     , "", lambda: _dpkglist(f.parser.part[1])),
    ("build-dep"      , "", lambda: _pkgnames(f.parser.part[1])),
    ("check"          , "", []),
    ("clean"          , "", []),
    ("dist-upgrade"   , "", []),
    ("dselect-upgrade", "", []),
    ("install"        , "", lambda: _pkgnames(f.parser.part[1])),
    ("purge"          , "", lambda: _dpkglist(f.parser.part[1])),
    ("remove"         , "", lambda: _dpkglist(f.parser.part[1])),
    ("source"         , "", lambda: _pkgnames(f.parser.part[1])),
    ("update"         , "", []),
    ("upgrade"        , "", []),
    ("help"           , "", []),
    )

def _aptcache_arguments(f): return (
    ("add"      , "", []),
    ("depends"  , "", lambda: _pkgnames(f.parser.part[1])),
    ("dotty"    , "", lambda: _pkgnames(f.parser.part[1])),
    ("dump"     , "", []),
    ("dumpavail", "", []),
    ("gencaches", "", []),
    ("help"     , "", []),
    ("madison"  , "", lambda: _pkgnames(f.parser.part[1])),
    ("pkgnames" , "", []),
    ("policy"   , "", lambda: _pkgnames(f.parser.part[1])),
    ("rdepends" , "", lambda: _pkgnames(f.parser.part[1])),
    ("search"   , "", []),
    ("show"     , "", lambda: _pkgnames(f.parser.part[1])),
    ("showpkg"  , "", lambda: _pkgnames(f.parser.part[1])),
    ("showsrc"  , "", lambda: _pkgnames(f.parser.part[1])),
    ("stats"    , "", []),
    ("unmet"    , "", []),
    ("xvcg"     , "", lambda: _pkgnames(f.parser.part[1])),
    )

def _pkgnames(s):
    try:
        out = subprocess.Popen(
            ["apt-cache", "pkgnames"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()[0]
    except Exception:
        return []
    try:
        out = out.decode()
    except UnicodeError:
        return []
    return [item for item in out.splitlines() if item.startswith(s)]

def _dpkglist(s):
    try:
        out = subprocess.Popen(
            ["dpkg", "-l"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()[0]
    except Exception:
        return []
    try:
        out = out.decode()
    except UnicodeError:
        return []
    return [line.split()[1] for line in out.splitlines()[5:]
            if len(line) > 2 and line[1].startswith(s)]

class AptGet(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _aptget_arguments(self)]

class AptCache(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _aptcache_arguments(self)]

completion.register("apt-get", AptGet)
completion.register("apt-cache", AptCache)
