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

class Process(object):
    shell = ("/bin/bash", "-c")
    terminal_emulator = ("x-terminal-emulator", "-e")

    def __init__(self):
        self.quick = False
        self.exterminal = False
        self.background = False

    def spawn(self, cmd, title=None):
        cmd = util.expandmacro(cmd, shell=True)
        cmd = self.parsemacro(cmd)
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

    def parsemacro(self, string):
        ret = string
        if re.search('(?!\\\\)%&', string):
            self.background = True
            ret = re.sub('(?!\\\\)%&', '', ret)
        if re.search('(?!\\\\)%q', string):
            self.quick = True
            ret = re.sub('(?!\\\\)%q', '', ret)
        if re.search('(?!\\\\)%T', string):
            self.exterminal = True
            ret = re.sub('(?!\\\\)%T', '', ret)
        return ret
