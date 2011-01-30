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

class AptGet(object):
    def __init__(self, comp):
        self.comp = comp
        self.arguments = {
            'autoclean'      : [],
            'autoremove'     : self.comp_dpkglist,
            'build-dep'      : self.comp_pkgnames,
            'check'          : [],
            'clean'          : [],
            'dist-upgrade'   : [],
            'dselect-upgrade': [],
            'install'        : self.comp_pkgnames,
            'purge'          : self.comp_dpkglist,
            'remove'         : self.comp_dpkglist,
            'source'         : self.comp_pkgnames,
            'update'         : [],
            'upgrade'        : [],
            'help'           : [],
            }

    def options(self):
        ret = [opt for opt in self.arguments.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def default(self):
        return self.options()

    def comp_pkgnames(self):
        (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        li = out.split(os.linesep)
        ret = [item for item in li if item.startswith(self.comp.parser.nowstr)]
        return ret

    def comp_dpkglist(self):
        (out, err) = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        pkgs = []
        for i, line in enumerate(out.split(os.linesep)):
            if i > 4:
                li = line.split()
                if len(li) > 2 and li[1].startswith(self.comp.parser.nowstr):
                    pkgs.append(li[1])
        return pkgs

    def complete(self):
        opt = self.comp.parser.current_option
        value = self.arguments.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

class AptCache(object):
    def __init__(self, comp):
        self.comp = comp
        self.arguments = {
            'add'      : [],
            'depends'  : self.comp_pkgnames,
            'dotty'    : self.comp_pkgnames,
            'dump'     : [],
            'dumpavail': [],
            'gencaches': [],
            'help'     : [],
            'madison'  : self.comp_pkgnames,
            'pkgnames' : [],
            'policy'   : self.comp_pkgnames,
            'rdepends' : self.comp_pkgnames,
            'search'   : [],
            'show'     : self.comp_pkgnames,
            'showpkg'  : self.comp_pkgnames,
            'showsrc'  : self.comp_pkgnames,
            'stats'    : [],
            'unmet'    : [],
            'xvcg'     : self.comp_pkgnames,
            }

    def default(self):
        return self.options()

    def options(self):
        ret = [opt for opt in self.arguments.keys()
               if opt.startswith(self.comp.parser.nowstr)
               and not opt in self.comp.parser.options]
        return sorted(ret)

    def comp_pkgnames(self):
        (out, err) = subprocess.Popen(["apt-cache", "pkgnames"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        li = out.split(os.linesep)
        ret = [item for item in li if item.startswith(self.comp.parser.nowstr)]
        return ret

    def complete(self):
        opt = self.comp.parser.current_option
        value = self.arguments.get(opt, self.default)

        if hasattr(value, "__call__"):
            return value()
        else:
            return value

from pyful.completion import optionsdict
optionsdict.update({"apt-get": AptGet,
                    "apt-cache": AptCache,
                    })
