# mode.py - cmdline's mode
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
import time

from pyfulib.core import Pyful
from pyfulib import filectrl
from pyfulib import process
from pyfulib import util

pyful = Pyful()

class Shell(object):
    prompt = '$'

    def complete(self, comp):
        return comp.comp_program_options()

    def execute(self, cmd):
        process.spawn(cmd)

class Eval(object):
    prompt = 'Eval:'

    def complete(self, comp):
        return comp.comp_python_builtin_functions()

    def execute(self, cmd):
        proc = process.Process()
        proc.python(proc.expandmacro(cmd, True))

class Mx(object):
    prompt = 'M-x'

    def complete(self, comp):
        return comp.comp_pyful_commands()

    def execute(self, cmd):
        from pyfulib.command import commands
        try:
            commands[cmd]()
        except Exception as e:
            pyful.message.error(str(e))

class ChangeWorkspaceTitle(object):
    prompt = 'Change workspace title:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        pyful.filer.workspace.chtitle(title)

class Chdir(object):
    prompt = 'Chdir to:'

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        pyful.filer.dir.chdir(path)

class Chmod(object):
    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return "Chmod mark files:"
        else:
            mode = "%o" % pyful.filer.file.stat.st_mode
            return "Chmod (%s - %s):" % (pyful.filer.file.name, mode)

    def complete(self, comp):
        pass

    def execute(self, mode):
        if pyful.filer.dir.ismark():
            for f in pyful.filer.dir.get_mark_files():
                filectrl.chmod(f, mode)
            pyful.filer.dir.mark_clear()
        else:
            filectrl.chmod(pyful.filer.file.name, mode)
        pyful.filer.workspace.all_reload()

class Chown(object):
    def __init__(self):
        self.user = None
        self.group = None

    @property
    def prompt(self):
        if self.user is None:
            return "User:"
        elif self.group is None:
            return "Group:"
        else:
            return "Chown:"

    def complete(self, comp):
        if self.user is None:
            return comp.comp_username()
        elif self.group is None:
            return comp.comp_groupname()

    def execute(self, string):
        if self.user is None:
            if string == "":
                self.user = -1
            else:
                self.user = string
            pyful.cmdline.restart("")
        else:
            if string == "":
                self.group = -1
            else:
                self.group = string
            filectrl.chown(pyful.filer.file.name, self.user, self.group)

class Copy(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return "Copy mark files to:"
        elif self.src:
            return "Copy from %s to:" % self.src
        elif self.src is None:
            return "Copy from:"
        else:
            return "Copy:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                pyful.message.error("Copy error: Destination is not directory")
                return
            filectrl.copy(pyful.filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            pyful.cmdline.restart(pyful.filer.workspace.nextdir.path)
        else:
            filectrl.copy(self.src, path)

class CreateWorkspace(object):
    prompt = "Create workspace (title):"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        pyful.filer.create_workspace(title)

class Delete(object):
    @property
    def prompt(self):
        return "Delete:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        msg = path.replace(pyful.filer.dir.path, "")
        ret = pyful.message.confirm("Delete? (%s):"%msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return
        filectrl.delete(path)
        pyful.filer.workspace.all_reload()

class Glob(object):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return "Glob pattern:"
        else:
            return "Glob pattern (default %s):" % self.default

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        if not self.default == "" and pattern == "":
            pyful.filer.dir.glob(self.default)
        else:
            if pattern == "":
                return
            Glob.default = pattern
            pyful.filer.dir.glob(pattern)

class GlobDir(object):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return "Glob dir pattern:"
        else:
            return "Glob dir pattern (default %s):" % self.default

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        if not self.default == "" and pattern == "":
            pyful.filer.dir.globdir(self.default)
        else:
            if pattern == "":
                return
            GlobDir.default = pattern
            pyful.filer.dir.globdir(pattern)

class Link(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return "Link mark files to:"
        elif self.src:
            return "Link from `%s' to:" % self.src
        elif self.src is None:
            return "Link from:"
        else:
            return "Link:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                pyful.message.error("Error: Destination is not directory")
                return
            for f in pyful.filer.dir.get_mark_files():
                dst = os.path.join(path, util.unix_basename(f))
                filectrl.link(f, dst)
            pyful.filer.dir.mark_clear()
            pyful.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            pyful.cmdline.restart(pyful.filer.workspace.nextdir.path)
        else:
            filectrl.link(self.src, path)
            pyful.filer.workspace.all_reload()

class Mark(object):
    default = None

    @property
    def prompt(self):
        if self.default:
            return "Mark pattern (%s):" % self.default.pattern
        else:
            return "Mark pattern:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        if self.default and pattern == "":
            pyful.filer.dir.mark(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except Exception as e:
                pyful.message.error("Regexp error: " + str(e))
                return
            self.__class__.default = reg
            pyful.filer.dir.mark(reg)

class Mask(object):
    default = None

    @property
    def prompt(self):
        if self.default:
            return "Mask pattern %s:" % self.default.pattern
        else:
            return "Mask pattern:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        if self.default and pattern == "":
            pyful.filer.dir.mask(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except:
                return pyful.message.error("Argument error: Can't complile `%s'" % pattern)
            self.__class__.default = reg
            pyful.filer.dir.mask(reg)

class Menu(object):
    prompt = 'Menu name:'

    def complete(self, comp):
        return list(pyful.menu.items.keys())

    def execute(self, name):
        pyful.menu.show(name)

class Mkdir(object):
    dirmode = 0o755
    prompt = "Make directory:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        filectrl.mkdir(path, self.dirmode)
        pyful.filer.workspace.all_reload()
        pyful.filer.dir.setcursor(pyful.filer.dir.get_index(util.unix_basename(path)))

class Move(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return "Move mark files to:"
        elif self.src:
            return "Move from %s to:" % self.src
        elif self.src is None:
            return "Move from:"
        else:
            return "Move:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                pyful.message.error("Move error: Destination is not directory")
                return
            filectrl.move(pyful.filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            pyful.cmdline.restart(pyful.filer.workspace.nextdir.path)
        else:
            filectrl.move(self.src, path)

class Newfile(object):
    filemode = 0o644
    prompt = "New file:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(util.abspath(path)):
            pyful.message.error("Error: file exists - %s" % path)
            return
        filectrl.mknod(path, self.filemode)
        pyful.filer.workspace.all_reload()
        pyful.filer.dir.setcursor(pyful.filer.dir.get_index(path))

class Rename(object):
    @property
    def prompt(self):
        return "Rename (%s):" % pyful.filer.file.name

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(path):
            pyful.message.error("Error: File exist - %s" % path)
            return

        try:
            os.renames(pyful.filer.file.name, path)
        except Exception as e:
            pyful.message.error("rename: %s" % e[1])
        pyful.filer.workspace.all_reload()

class Replace(object):
    default = []
    pattern = None

    @property
    def prompt(self):
        if self.pattern is None and self.default:
            return "Replace regexp (default %s -> %s):" % (self.default[0].pattern, self.default[1])
        elif self.pattern is None:
            return "Replace pattern:"
        else:
            return "Replace regexp %s with:" % self.pattern.pattern

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        if not pattern and not self.pattern and self.default:
            filectrl.replace(self.default[0], self.default[1])
            pyful.filer.dir.mark_clear()
            pyful.filer.workspace.all_reload()
        elif self.pattern is None:
            try:
                self.pattern = re.compile(pattern)
            except Exception:
                return pyful.message.error("Argument error: Can't complile `%s'" % pattern)
            pyful.cmdline.restart("")
        else:
            filectrl.replace(self.pattern, pattern)
            Replace.default[:] = []
            Replace.default.append(self.pattern)
            Replace.default.append(pattern)
            pyful.filer.dir.mark_clear()
            pyful.filer.workspace.all_reload()

class Symlink(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return "Symlink mark files to:"
        elif self.src:
            return "Symlink from `%s' to:" % self.src
        elif self.src is None:
            return "Symlink from:"
        else:
            return "Symlink:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                pyful.message.error("Symlink error: Destination is not directory")
                return
            for f in pyful.filer.dir.get_mark_files():
                dst = os.path.join(path, os.path.basename(f))
                filectrl.symlink(f, dst)
            pyful.filer.dir.mark_clear()
            pyful.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            pyful.cmdline.restart(pyful.filer.workspace.nextdir.path)
        else:
            filectrl.symlink(self.src, path)
            pyful.filer.workspace.all_reload()

class TrashBox(object):
    prompt = "Trashbox:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        trashbox = os.path.expanduser(pyful.environs['TRASHBOX'])
        msg = path.replace(pyful.filer.dir.path, "")
        ret = pyful.message.confirm("Move `%s' to trashbox? " % msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return

        filectrl.move(path, trashbox)
        pyful.filer.workspace.all_reload()

class Utime(object):
    def __init__(self):
        self.sttime = []
        self.path = None
        self.timesec = None

    @property
    def prompt(self):
        if not self.path:
            return "Utime path:"
        elif len(self.sttime) == 0:
            return "Utime year: %s ->" % self.timesec[0]
        elif len(self.sttime) == 1:
            return "Utime month: %s ->" % self.timesec[1]
        elif len(self.sttime) == 2:
            return "Utime day: %s ->" % self.timesec[2]
        elif len(self.sttime) == 3:
            return "Utime hour: %s ->" % self.timesec[3]
        elif len(self.sttime) == 4:
            return "Utime min: %s ->" % self.timesec[4]
        elif len(self.sttime) == 5:
            return "Utime sec: %s ->" % self.timesec[5]

    def complete(self, comp):
        if not self.path:
            return comp.comp_files()
        elif len(self.sttime) == 0:
            return []
        elif len(self.sttime) == 1:
            return [str(i) for i in range(1, 13)]
        elif len(self.sttime) == 2:
            return [str(i) for i in range(1, 32)]
        elif len(self.sttime) == 3:
            return [str(i) for i in range(0, 24)]
        elif len(self.sttime) == 4:
            return [str(i) for i in range(0, 60)]
        elif len(self.sttime) == 5:
            return [str(i) for i in range(0, 62)]

    def execute(self, st):
        if not self.path:
            if os.path.exists(st):
                self.path = st
                self.timesec = time.localtime(os.stat(self.path).st_mtime)
                pyful.cmdline.restart("")
            else:
                return pyful.message.error("%s doesn't exist." % st)

        elif len(self.sttime) == 0:
            if st == "":
                self.sttime.append(self.timesec[0])
            else:
                self.sttime.append(int(st))
            pyful.cmdline.restart("")
        elif len(self.sttime) == 1:
            if st == "":
                self.sttime.append(self.timesec[1])
            elif 0 < int(st) <= 12:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[1])
            pyful.cmdline.restart("")
        elif len(self.sttime) == 2:
            if st == "":
                self.sttime.append(self.timesec[2])
            elif 0 < int(st) <= 31:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[2])
            pyful.cmdline.restart("")
        elif len(self.sttime) == 3:
            if st == "":
                self.sttime.append(self.timesec[3])
            elif 0 <= int(st) <= 23:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[3])
            pyful.cmdline.restart("")
        elif len(self.sttime) == 4:
            if st == "":
                self.sttime.append(self.timesec[4])
            elif 0 <= int(st) <= 59:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[4])
            pyful.cmdline.restart("")
        elif len(self.sttime) == 5:
            if st == "":
                self.sttime.append(self.timesec[5])
            elif 0 <= int(st) <= 61:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[6])

            self.sttime += [-1, -1, -1]
            try:
                atime = mtime = time.mktime(tuple(self.sttime))
                os.utime(self.path, (atime, mtime))
            except Exception as e:
                pyful.message.error(str(e))
            pyful.filer.workspace.all_reload()

class UnZip(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            return 'Mark files unzip to:'
        elif self.src is None:
            return 'Unzip from:'
        else:
            return 'Unzip from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            filectrl.unzip(pyful.filer.dir.get_mark_files(), path)
            pyful.filer.dir.mark_clear()
            pyful.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            pyful.cmdline.restart(pyful.filer.workspace.nextdir.path)
        else:
            filectrl.unzip(self.src, path)
            pyful.filer.workspace.all_reload()

class Zip(object):
    def __init__(self):
        self.src = None
        self.wrap = None

    @property
    def prompt(self):
        if pyful.filer.dir.ismark():
            if self.wrap is None:
                return 'Mark files wrap is:'
            else:
                return 'Mark files zip to:'
        elif self.src is None:
            return 'Zip from:'
        else:
            return 'Zip from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if pyful.filer.dir.ismark():
            if self.wrap is None:
                self.wrap = path
                ext = '.zip'
                zippath = os.path.join(pyful.filer.workspace.nextdir.path, self.wrap + ext)
                pyful.cmdline.restart(zippath, -len(ext))
            else:
                filectrl.zip(pyful.filer.dir.get_mark_files(), path, self.wrap)
                pyful.filer.dir.mark_clear()
                pyful.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = '.zip'
            zippath = os.path.join(pyful.filer.workspace.nextdir.path, self.src + ext)
            pyful.cmdline.restart(zippath, -len(ext))
        else:
            filectrl.zip(self.src, path)
            pyful.filer.workspace.all_reload()
