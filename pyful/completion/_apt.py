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

import os
import subprocess

from pyful.completion import CompletionFunction
from pyful.completion import optionsdict

def comp_pkgnames(nowstr):
    (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    li = out.split(os.linesep)
    ret = [item for item in li if item.startswith(nowstr)]
    return ret

def comp_dpkglist(nowstr):
    (out, err) = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    pkgs = []
    for i, line in enumerate(out.split(os.linesep)):
        if i > 4:
            li = line.split()
            if len(li) > 2 and li[1].startswith(nowstr):
                pkgs.append(li[1])
    return pkgs

class AptGet(CompletionFunction):
    def __init__(self, comp):
        arguments = {
            'autoclean'      : [],
            'autoremove'     : lambda: comp_dpkglist(self.comp.parser.nowstr),
            'build-dep'      : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'check'          : [],
            'clean'          : [],
            'dist-upgrade'   : [],
            'dselect-upgrade': [],
            'install'        : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'purge'          : lambda: comp_dpkglist(self.comp.parser.nowstr),
            'remove'         : lambda: comp_dpkglist(self.comp.parser.nowstr),
            'source'         : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'update'         : [],
            'upgrade'        : [],
            'help'           : [],
            }
        CompletionFunction.__init__(self, comp, arguments)

class AptCache(CompletionFunction):
    def __init__(self, comp):
        arguments = {
            'add'      : [],
            'depends'  : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'dotty'    : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'dump'     : [],
            'dumpavail': [],
            'gencaches': [],
            'help'     : [],
            'madison'  : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'pkgnames' : [],
            'policy'   : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'rdepends' : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'search'   : [],
            'show'     : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'showpkg'  : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'showsrc'  : lambda: comp_pkgnames(self.comp.parser.nowstr),
            'stats'    : [],
            'unmet'    : [],
            'xvcg'     : lambda: comp_pkgnames(self.comp.parser.nowstr),
            }
        CompletionFunction.__init__(self, comp, arguments)

optionsdict.update({"apt-get": AptGet,
                    "apt-cache": AptCache,
                    })
