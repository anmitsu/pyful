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
from pyful.completion import Argument, Candidate

def _aptget_arguments(f): return (
    ("autoclean"      , "", []),
    ("autoremove"     , "", _dpkglist),
    ("build-dep"      , "", _pkgnames),
    ("check"          , "", []),
    ("clean"          , "", []),
    ("dist-upgrade"   , "", []),
    ("dselect-upgrade", "", []),
    ("install"        , "", _pkgnames),
    ("purge"          , "", _dpkglist),
    ("remove"         , "", _dpkglist),
    ("source"         , "", _pkgnames),
    ("update"         , "", []),
    ("upgrade"        , "", []),
    ("help"           , "", []),
    )

def _aptcache_arguments(f): return (
    ("add"      , "", []),
    ("depends"  , "", _pkgnames),
    ("dotty"    , "", _pkgnames),
    ("dump"     , "", []),
    ("dumpavail", "", []),
    ("gencaches", "", []),
    ("help"     , "", []),
    ("madison"  , "", _pkgnames),
    ("pkgnames" , "", []),
    ("policy"   , "", _pkgnames),
    ("rdepends" , "", _pkgnames),
    ("search"   , "", []),
    ("show"     , "", _pkgnames),
    ("showpkg"  , "", _pkgnames),
    ("showsrc"  , "", _pkgnames),
    ("stats"    , "", []),
    ("unmet"    , "", []),
    ("xvcg"     , "", _pkgnames),
    )

def _pkgnames():
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
    return out.splitlines()

def _dpkglist():
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
    candidates = []
    vermax = max(len(line.split()[2]) for line in out.splitlines()[5:])
    for line in out.splitlines()[5:]:
        info = line.split()
        version = info[2]
        description = " ".join(info[3:])
        doc = "-- v{0:<{1}}{2}".format(version, vermax, description)
        candidates.append(Candidate(names=info[1], doc=doc))
    return candidates

class AptGet(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _aptget_arguments(self)]

class AptCache(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _aptcache_arguments(self)]

completion.register("apt-get", AptGet)
completion.register("apt-cache", AptCache)
