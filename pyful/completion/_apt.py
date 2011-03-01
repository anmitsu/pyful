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

from pyful.completion import CompletionFunction
from pyful.completion import optionsdict

def comp_pkgnames(s):
    (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    li = out.split(os.linesep)
    ret = [item for item in li if item.startswith(s)]
    return ret

def comp_dpkglist(s):
    (out, err) = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    pkgs = []
    for i, line in enumerate(out.split(os.linesep)):
        if i > 4:
            li = line.split()
            if len(li) > 2 and li[1].startswith(s):
                pkgs.append(li[1])
    return pkgs

class AptGet(CompletionFunction):
    def __init__(self, comp):
        arguments = {
            'autoclean'      : [],
            'autoremove'     : lambda: comp_dpkglist(self.comp.parser.part[1]),
            'build-dep'      : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'check'          : [],
            'clean'          : [],
            'dist-upgrade'   : [],
            'dselect-upgrade': [],
            'install'        : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'purge'          : lambda: comp_dpkglist(self.comp.parser.part[1]),
            'remove'         : lambda: comp_dpkglist(self.comp.parser.part[1]),
            'source'         : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'update'         : [],
            'upgrade'        : [],
            'help'           : [],
            }
        CompletionFunction.__init__(self, comp, arguments)

class AptCache(CompletionFunction):
    def __init__(self, comp):
        arguments = {
            'add'      : [],
            'depends'  : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'dotty'    : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'dump'     : [],
            'dumpavail': [],
            'gencaches': [],
            'help'     : [],
            'madison'  : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'pkgnames' : [],
            'policy'   : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'rdepends' : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'search'   : [],
            'show'     : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'showpkg'  : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'showsrc'  : lambda: comp_pkgnames(self.comp.parser.part[1]),
            'stats'    : [],
            'unmet'    : [],
            'xvcg'     : lambda: comp_pkgnames(self.comp.parser.part[1]),
            }
        CompletionFunction.__init__(self, comp, arguments)

optionsdict.update({"apt-get": AptGet,
                    "apt-cache": AptCache,
                    })
