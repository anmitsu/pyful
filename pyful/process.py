# process.py - process management
#
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
import re
import curses
from subprocess import Popen, PIPE

from pyful import Pyful, setsignal, resetsignal
from pyful import util
from pyful import message

def spawn(cmd, title=None, expandmacro=True):
    if expandmacro:
        cmd = util.expandmacro(cmd, shell=True)
    Process().spawn(cmd, title)

def python(cmd):
    cmd = util.expandmacro(cmd, shell=False)
    Process().python(cmd)

def system(cmd):
    Process().system(cmd)

def view_process():
    for p in Process.procs:
        poll = p.poll()
        if poll == 0:
            Process.procs.remove(p)
        elif poll != None:
            (out, err) = p.communicate()
            if err:
                message.error(err)
            Process.procs.remove(p)

class Process(object):
    shell = ("/bin/bash", "-c")
    terminal_emulator = ("x-terminal-emulator", "-e")
    procs = []

    def __init__(self):
        self.quick = False
        self.exterminal = False
        self.background = False

    def spawn(self, cmd, title=None):
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
        cmd = self.parsemacro(cmd)
        curses.endwin()
        os.system("clear")
        try:
            exec(cmd)
            message.puts("Eval: %s" % cmd)
            if not self.quick:
                util.wait_restore()
        except Exception as e:
            message.exception(e)

    def system(self, cmd):
        if self.background:
            try:
                proc = Popen(cmd, shell=True, executable=self.shell[0],
                             close_fds=True, preexec_fn=os.setsid, stdout=PIPE, stderr=PIPE)
                self.procs.append(proc)
                message.puts("Spawn: %s (%s)" % (cmd.strip(), proc.pid))
            except Exception as e:
                message.exception(e)
        else:
            curses.endwin()
            os.system("clear")
            try:
                resetsignal()
                proc = Popen(cmd, shell=True, executable=self.shell[0],
                             close_fds=True, preexec_fn=os.setsid)
                proc.wait()
                if not self.quick:
                    util.wait_restore()
                message.puts("Spawn: %s (%s)" % (cmd.strip(), proc.pid))
            except Exception as e:
                message.exception(e)
            finally:
                setsignal()

    def screen(self, cmd, title):
        Popen(["screen", "-t", title, self.shell[0], self.shell[1], "%s; python %s -e" % (cmd, Pyful.binpath)])
        message.puts("Spawn: %s (screen)" % cmd.strip())

    def terminal(self, cmd):
        Popen([self.terminal_emulator[0], self.terminal_emulator[1], cmd])
        message.puts("Spawn: %s (%s)" % (cmd.strip(), self.terminal_emulator[0]))

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
