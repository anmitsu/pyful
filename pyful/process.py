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

import threading
import os
import re
import sys
from subprocess import Popen, PIPE

from pyful import message
from pyful import util
from pyful import widget

def spawn(cmd, title=None, expandmacro=True):
    if expandmacro:
        cmd = util.expandmacro(cmd, shell=True)
    Process().spawn(cmd, title)

def python(cmd):
    cmd = util.expandmacro(cmd, shell=False)
    Process().python(cmd)

def system(cmd):
    Process().system(cmd)

class Process(object):
    shell = ("/bin/bash", "-c")
    terminal_emulator = ("x-terminal-emulator", "-e")
    screen_command = ("screen", "-t", "{TITLE}", "bash", "-c", "{COMMAND}")

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
        elif "screen" in os.getenv("TERM") and not self.background:
            if len(cmd) > 4000:
                self.system(cmd)
            else:
                self.screen(cmd, title)
        else:
            self.system(cmd)

    def python(self, cmd):
        cmd = self.parsemacro(cmd)
        try:
            widget.end_curses()
            os.system("clear")
            exec(cmd)
            if not self.quick:
                util.wait_restore()
            message.puts("Eval: {0}".format(cmd))
        except KeyboardInterrupt as e:
            message.error("KeyboardInterrupt: {0}".format(cmd))
        except Exception as e:
            message.exception(e)
        finally:
            widget.start_curses()

    def system(self, cmd):
        if self.background:
            try:
                proc = Popen(cmd, shell=True, executable=self.shell[0],
                             close_fds=True, preexec_fn=os.setsid, stdout=PIPE, stderr=PIPE)
                message.puts("Spawn: {0} ({1})".format(cmd.strip(), proc.pid))
                ProcessNotify(proc, cmd).start()
            except Exception as e:
                message.exception(e)
        else:
            try:
                widget.end_curses()
                os.system("clear")
                proc = Popen(cmd, shell=True, executable=self.shell[0],
                             close_fds=True, preexec_fn=os.setsid)
                proc.wait()
                if not self.quick:
                    util.wait_restore()
                message.puts("Spawn: {0} ({1})".format(cmd.strip(), proc.pid))
            except KeyboardInterrupt as e:
                message.error("KeyboardInterrupt: {0}".format(cmd))
            except Exception as e:
                message.exception(e)
            finally:
                widget.start_curses()

    def screen(self, cmd, title):
        if not self.quick:
            cmd = "{0}; {1} -e".format(cmd, sys.argv[0])
        command = [arg.format(TITLE=title, COMMAND=cmd) for arg in self.screen_command]
        Popen(command)
        message.puts("Spawn: {0} (screen)".format(cmd.strip()))

    def terminal(self, cmd):
        command = []
        command.extend(self.terminal_emulator)
        command.append(cmd)
        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        message.puts("Spawn: {0} ({1})".format(cmd.strip(), self.terminal_emulator[0]))
        ProcessNotify(proc, cmd).start()

    def parsemacro(self, string):
        ret = string
        if re.search(r"(?!\\)%&", string):
            self.background = True
            ret = re.sub(r"(?!\\)%&", "", ret)
        if re.search(r"(?!\\)%q", string):
            self.quick = True
            ret = re.sub(r"(?!\\)%q", "", ret)
        if re.search(r"(?!\\)%T", string):
            self.exterminal = True
            ret = re.sub(r"(?!\\)%T", "", ret)
        return ret

class ProcessNotify(threading.Thread):
    def __init__(self, proc, name):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.proc = proc
        self.name = name.strip()

    def run(self):
        out, err = self.proc.communicate()
        if out:
            self.notify_output(out)
        if err:
            self.notify_error(err)
        if out or err:
            message.forcedraw()

    def notify_output(self, out):
        for line in out.splitlines():
            if not line:
                continue
            try:
                line = line.decode()
                message.puts("{0} - ({1})".format(line, self.name))
            except UnicodeError:
                line = "????? - Invalid encoding"
                message.error("{0} - ({1})".format(line, self.name))

    def notify_error(self, err):
        for line in err.splitlines():
            if not line:
                continue
            try:
                line = line.decode()
            except UnicodeError:
                line = "????? - Invalid encoding"
            message.error("{0} - ({1})".format(line, self.name))
