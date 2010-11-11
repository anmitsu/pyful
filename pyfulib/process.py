# process.py - process management
#
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
import re
import curses
import subprocess

from pyfulib import util
from pyfulib.core import Pyful

pyful = Pyful()

def spawn(cmd, title=None):
    Process().spawn(cmd, title)

def python(cmd):
    Process().python(cmd)

def system(cmd):
    Process().system(cmd)

def expandmacro(string, flg):
    return Process().expandmacro(string, flg)

class Process(object):
    shell = ("/bin/bash", "-c")
    terminal_emulator = ("x-terminal-emulator", "-e")

    def __init__(self):
        self.quick = False
        self.exterminal = False
        self.background = False

    def spawn(self, cmd, title=None):
        cmd = self.expandmacro(cmd, True)
        if title is None:
            title = cmd
        if self.exterminal and not self.background:
            self.terminal(cmd)
        elif "screen" in os.environ['TERM'] and not self.background:
            if len(cmd) > 4000:
                self.system(cmd)
            else:
                self.screen(cmd, title)
        else:
            self.system(cmd)

    def python(self, cmd):
        curses.endwin()
        os.system("clear")
        try:
            exec(cmd)
            util.wait_restore()
        except Exception as e:
            pyful.message.exception(e)

    def system(self, cmd):
        if self.background:
            cmd += " 1>%s 2>%s &" % (os.devnull, os.devnull)
        else:
            curses.endwin()
            os.system("clear")
        try:
            pyful.resetsignal()
            subprocess.call(cmd, shell=True)
            if self.quick or self.background:
                pass
            else:
                util.wait_restore()
        except Exception as e:
            pyful.message.exception(e)
        except KeyboardInterrupt as e:
            pass
        finally:
            pyful.setsignal()

    def screen(self, cmd, title):
        subprocess.Popen(["screen", "-t", title, self.shell[0], self.shell[1], "%s; python %s -e" % (cmd, pyful.binpath)])

    def terminal(self, cmd):
        subprocess.Popen([self.terminal_emulator[0], self.terminal_emulator[1], cmd])

    def expandmacro(self, string, flg):
        self.quick = False
        self.background = False
        self.exterminal = False
        ret = ""
        squote = False
        dquote = False

        i = 0
        while i < len(string):
            c = string[i]
            if "'" == c:
                if not dquote:
                    squote = not squote
                    ret += "'"
            elif '"' == c:
                if not squote:
                    dquote = not dquote
                    ret += '"'
            elif "%" == c and not dquote and not squote:
                i += 1
                c_next = string[i]
                if "q" == c_next:
                    if flg:
                        self.quick = True
                    else:
                        ret += "%q"
                elif "&" == c_next:
                    if flg:
                        self.background = True
                    else:
                        ret += "%&"
                elif "T" == c_next:
                    if flg:
                        self.exterminal = True
                    else:
                        ret += "%T"
                elif "m" == c_next:
                    if flg:
                        for f in pyful.filer.dir.get_mark_files():
                            ret += util.string_to_safe(f) + " "
                    else:
                        ret += "%m"
                elif "M" == c_next:
                    if flg:
                        for f in pyful.filer.dir.get_mark_files():
                            ret += util.abspath(util.string_to_safe(f)) + " "
                    else:
                        ret += "%M"
                elif "d" == c_next:
                    try:
                        string[i+1]
                    except IndexError:
                        path = util.unix_basename(pyful.filer.dir.path) + os.sep
                        ret += util.quote(path)
                        i += 1
                        continue
                    if "2" == string[i+1]:
                        i += 1
                        path = util.unix_basename(pyful.filer.workspace.nextdir.path) + os.sep
                        ret += util.quote(path)
                    else:
                        path = util.unix_basename(pyful.filer.dir.path) + os.sep
                        ret += util.quote(path)
                elif "D" == c_next:
                    try:
                        string[i+1]
                    except IndexError:
                        ret += util.quote(pyful.filer.dir.path)
                        i += 1
                        continue
                    if "2" == string[i+1]:
                        i += 1
                        ret += util.quote(pyful.filer.workspace.nextdir.path)
                    else:
                        ret += util.quote(pyful.filer.dir.path)
                elif "f" == c_next:
                    ret += util.quote(pyful.filer.file.name)
                elif "F" == c_next:
                    path = util.abspath(pyful.filer.file.name)
                    ret += util.quote(path)
                elif "x" == c_next:
                    fname = util.unix_basename(pyful.filer.file.name)
                    ext = util.extname(pyful.filer.file.name)
                    ret += util.quote(fname.replace(ext, ""))
                elif "X" == c_next:
                    fname = util.unix_basename(pyful.filer.file.name)
                    ext = util.extname(pyful.filer.file.name)
                    fname = util.abspath(fname)
                    ret += util.quote(fname.replace(ext, ""))
                else:
                    ret += "%" + c_next
            else:
                ret += c
            i += 1
        return ret
