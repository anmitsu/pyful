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

from pyful.core import Pyful
from pyful import filectrl
from pyful import process
from pyful import util

core = Pyful()

class Shell(object):
    prompt = '$'

    def complete(self, comp):
        return comp.comp_program_options()

    def execute(self, cmd):
        process.spawn(cmd, expandmacro=False)

class Eval(object):
    prompt = 'Eval:'

    def complete(self, comp):
        return comp.comp_python_builtin_functions()

    def execute(self, cmd):
        process.python(cmd)

class Mx(object):
    prompt = 'M-x'

    def complete(self, comp):
        return comp.comp_pyful_commands()

    def execute(self, cmd):
        from pyful.command import commands
        try:
            commands[cmd]()
        except KeyError:
            core.message.error("Undefined command `%s'" % cmd)

class ChangeWorkspaceTitle(object):
    prompt = 'Change workspace title:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        core.filer.workspace.chtitle(title)

class Chdir(object):
    prompt = 'Chdir to:'

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        core.filer.dir.chdir(path)

class Chmod(object):
    @property
    def prompt(self):
        if core.filer.dir.ismark():
            return "Chmod mark files:"
        else:
            mode = "%o" % core.filer.file.stat.st_mode
            return "Chmod (%s - %s):" % (core.filer.file.name, mode)

    def complete(self, comp):
        pass

    def execute(self, mode):
        if core.filer.dir.ismark():
            for f in core.filer.dir.get_mark_files():
                filectrl.chmod(f, mode)
        else:
            filectrl.chmod(core.filer.file.name, mode)
        core.filer.workspace.all_reload()

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
            core.cmdline.restart("")
        else:
            if string == "":
                self.group = -1
            else:
                self.group = string
            filectrl.chown(core.filer.file.name, self.user, self.group)

class Copy(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
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
        if core.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                core.message.error("Copy error: Destination is not directory")
                return
            filectrl.copy(core.filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.copy(self.src, path)

class CreateWorkspace(object):
    prompt = "Create workspace (title):"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        core.filer.create_workspace(title)

class Delete(object):
    @property
    def prompt(self):
        return "Delete:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        msg = path.replace(core.filer.dir.path, "")
        ret = core.message.confirm("Delete? (%s):"%msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return
        filectrl.delete(path)
        core.filer.workspace.all_reload()

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
            core.filer.dir.glob(self.default)
        else:
            if pattern == "":
                return
            Glob.default = pattern
            core.filer.dir.glob(pattern)

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
            core.filer.dir.globdir(self.default)
        else:
            if pattern == "":
                return
            GlobDir.default = pattern
            core.filer.dir.globdir(pattern)

class Link(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
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
        if core.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                core.message.error("Error: Destination is not directory")
                return
            for f in core.filer.dir.get_mark_files():
                dst = os.path.join(path, util.unix_basename(f))
                filectrl.link(f, dst)
            core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.link(self.src, path)
            core.filer.workspace.all_reload()

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
            core.filer.dir.mark(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except Exception as e:
                core.message.error("Regexp error: " + str(e))
                return
            self.__class__.default = reg
            core.filer.dir.mark(reg)

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
            core.filer.dir.mask(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except:
                return core.message.error("Argument error: Can't complile `%s'" % pattern)
            self.__class__.default = reg
            core.filer.dir.mask(reg)

class Menu(object):
    prompt = 'Menu name:'

    def complete(self, comp):
        return list(core.menu.items.keys())

    def execute(self, name):
        core.menu.show(name)

class Mkdir(object):
    dirmode = 0o755
    prompt = "Make directory:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        filectrl.mkdir(path, self.dirmode)
        core.filer.workspace.all_reload()
        core.filer.dir.setcursor(core.filer.dir.get_index(util.unix_basename(path)))

class Move(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
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
        if core.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                core.message.error("Move error: Destination is not directory")
                return
            filectrl.move(core.filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.move(self.src, path)

class Newfile(object):
    filemode = 0o644
    prompt = "New file:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(util.abspath(path)):
            core.message.error("Error: file exists - %s" % path)
            return
        filectrl.mknod(path, self.filemode)
        core.filer.workspace.all_reload()
        core.filer.dir.setcursor(core.filer.dir.get_index(path))

class OpenListfile(object):
    prompt = 'Open list file:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(path):
            core.filer.dir.open_listfile(path)
        else:
            core.message.error('No such list file: ' + path)

class Rename(object):
    def __init__(self, path=None):
        if path is None:
            self.path = core.filer.file.name
        else:
            self.path = path

    @property
    def prompt(self):
        try:
            util.unistr(self.path)
            return "Rename (%s):" % self.path
        except UnicodeError:
            return "Rename invalid encoding to:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(path):
            core.message.error("Error: File exist - %s" % path)
            return

        try:
            os.renames(self.path, path)
        except Exception as e:
            core.message.exception(e)
        core.filer.workspace.all_reload()

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
            core.filer.dir.mark_clear()
            core.filer.workspace.all_reload()
        elif self.pattern is None:
            try:
                self.pattern = re.compile(util.unistr(pattern))
            except Exception:
                return core.message.error("Argument error: Can't complile `%s'" % pattern)
            core.cmdline.restart("")
        else:
            filectrl.replace(self.pattern, pattern)
            Replace.default[:] = []
            Replace.default.append(self.pattern)
            Replace.default.append(pattern)
            core.filer.dir.mark_clear()
            core.filer.workspace.all_reload()

class Symlink(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
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
        if core.filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                core.message.error("Symlink error: Destination is not directory")
                return
            for f in core.filer.dir.get_mark_files():
                dst = os.path.join(path, os.path.basename(f))
                filectrl.symlink(f, dst)
            core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.symlink(self.src, path)
            core.filer.workspace.all_reload()

class TrashBox(object):
    prompt = "Trashbox:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        trashbox = os.path.expanduser(core.environs['TRASHBOX'])
        msg = path.replace(core.filer.dir.path, "")
        ret = core.message.confirm("Move `%s' to trashbox? " % msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return

        filectrl.move(path, trashbox)
        core.filer.workspace.all_reload()

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
                core.cmdline.restart("")
            else:
                return core.message.error("%s doesn't exist." % st)

        elif len(self.sttime) == 0:
            if st == "":
                self.sttime.append(self.timesec[0])
            else:
                self.sttime.append(int(st))
            core.cmdline.restart("")
        elif len(self.sttime) == 1:
            if st == "":
                self.sttime.append(self.timesec[1])
            elif 0 < int(st) <= 12:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[1])
            core.cmdline.restart("")
        elif len(self.sttime) == 2:
            if st == "":
                self.sttime.append(self.timesec[2])
            elif 0 < int(st) <= 31:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[2])
            core.cmdline.restart("")
        elif len(self.sttime) == 3:
            if st == "":
                self.sttime.append(self.timesec[3])
            elif 0 <= int(st) <= 23:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[3])
            core.cmdline.restart("")
        elif len(self.sttime) == 4:
            if st == "":
                self.sttime.append(self.timesec[4])
            elif 0 <= int(st) <= 59:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[4])
            core.cmdline.restart("")
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
                core.message.error(str(e))
            core.filer.workspace.all_reload()

class Tar(object):
    def __init__(self, tarmode, each=False):
        self.src = None
        self.wrap = None
        self.tarmode = tarmode
        self.each = each

    @property
    def prompt(self):
        if core.filer.dir.ismark() or self.each:
            if self.wrap is None:
                return 'Mark files wrap is:'
            else:
                if self.each:
                    return 'Mark files %s each to:' % self.tarmode
                else:
                    return 'Mark files %s to:' % self.tarmode
        elif self.src is None:
            return '%s from:' % self.tarmode
        else:
            return '%s from %s to:' % (self.tarmode, self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if core.filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    core.cmdline.restart(core.filer.workspace.nextdir.path)
                else:
                    ext = filectrl.TarThread.tarexts[self.tarmode]
                    tarpath = os.path.join(core.filer.workspace.nextdir.path, self.wrap + ext)
                    core.cmdline.restart(tarpath, -len(ext))
            else:
                if self.each:
                    filectrl.tareach(core.filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                else:
                    filectrl.tar(core.filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = filectrl.TarThread.tarexts[self.tarmode]
            tarpath = os.path.join(core.filer.workspace.nextdir.path, self.src + ext)
            core.cmdline.restart(tarpath, -len(ext))
        else:
            filectrl.tar(self.src, path, self.tarmode)
            core.filer.workspace.all_reload()

class UnTar(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
            return 'Mark files untar to:'
        elif self.src is None:
            return 'Untar from:'
        else:
            return 'Untar from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if core.filer.dir.ismark():
            filectrl.untar(core.filer.dir.get_mark_files(), path)
            core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.untar(self.src, path)
            core.filer.workspace.all_reload()

class WebSearch(object):
    def __init__(self, engine='Google'):
        self.engine = engine

    @property
    def prompt(self):
        return '%s search:' % self.engine

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, word):
        import webbrowser
        if self.engine == 'Google':
            word = word.replace(' ', '+')
            search = 'http://www.google.com/search?&q=%s' % word
        else:
            pass
        try:
            webbrowser.open(search, new=2)
        except Exception as e:
            core.message.exception(e)

class Zip(object):
    def __init__(self, each=False):
        self.src = None
        self.wrap = None
        self.each = each

    @property
    def prompt(self):
        if core.filer.dir.ismark() or self.each:
            if self.wrap is None:
                return 'Mark files wrap is:'
            else:
                if self.each:
                    return 'Mark files zip each to:'
                else:
                    return 'Mark files zip to:'
        elif self.src is None:
            return 'Zip from:'
        else:
            return 'Zip from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if core.filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    core.cmdline.restart(core.filer.workspace.nextdir.path)
                else:
                    ext = '.zip'
                    zippath = os.path.join(core.filer.workspace.nextdir.path, self.wrap + ext)
                    core.cmdline.restart(zippath, -len(ext))
            else:
                if self.each:
                    filectrl.zipeach(core.filer.dir.get_mark_files(), path, self.wrap)
                else:
                    filectrl.zip(core.filer.dir.get_mark_files(), path, self.wrap)
                core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = '.zip'
            zippath = os.path.join(core.filer.workspace.nextdir.path, self.src + ext)
            core.cmdline.restart(zippath, -len(ext))
        else:
            filectrl.zip(self.src, path)
            core.filer.workspace.all_reload()

class UnZip(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if core.filer.dir.ismark():
            return 'Mark files unzip to:'
        elif self.src is None:
            return 'Unzip from:'
        else:
            return 'Unzip from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if core.filer.dir.ismark():
            filectrl.unzip(core.filer.dir.get_mark_files(), path)
            core.filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            core.cmdline.restart(core.filer.workspace.nextdir.path)
        else:
            filectrl.unzip(self.src, path)
            core.filer.workspace.all_reload()

class ZoomInfoBox(object):
    prompt = 'Zoom infobox:'

    def complete(self, comp):
        return [str(x*10) for x in range(-10, 11)]

    def execute(self, zoom):
        from pyful import ui
        try:
            zoom = int(zoom)
            ui.zoom_infobox(zoom)
        except ValueError as e:
            core.message.exception(e)