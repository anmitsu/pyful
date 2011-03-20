# mode.py - cmdline's mode
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

import errno
import os
import re
import time

from pyful import Pyful
from pyful import filectrl
from pyful import look
from pyful import message
from pyful import process
from pyful import ui
from pyful import util

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
            message.error("Undefined command `{0}'".format(cmd))

class ChangeLooks(object):
    prompt = "Change looks:"

    def complete(self, comp):
        return sorted([l for l in look.looks.keys() if l.startswith(comp.parser.part[1])])

    def execute(self, name):
        if name in look.looks:
            Pyful.environs['LOOKS'] = look.looks[name]
            look.init_colors()
            ui.refresh()
        else:
            message.error("`{0}' looks doesn't exist".format(name))

class ChangeWorkspaceTitle(object):
    prompt = 'Change workspace title:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        ui.getcomponent("Filer").workspace.chtitle(title)

class Chdir(object):
    prompt = 'Chdir to:'

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        ui.getcomponent("Filer").dir.chdir(path)

class Chmod(object):
    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            return "Chmod mark files:"
        else:
            return "Chmod ({0} - {1:#o}):".format(filer.file.name, filer.file.stat.st_mode)

    def complete(self, comp):
        symbols = ['+r', '-r', '+w', '-w', '+x', '-x']
        return sorted([symb for symb in symbols if symb.startswith(comp.parser.part[1])])

    def execute(self, mode):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            for f in filer.dir.get_mark_files():
                mode = self._getmode(os.stat(f), mode)
                filectrl.chmod(f, mode)
        else:
            mode = self._getmode(filer.file.stat, mode)
            filectrl.chmod(filer.file.name, mode)
        filer.workspace.all_reload()

    def _getmode(self, st, mode):
        if mode == '+r':
            return "{0:#o}".format(st.st_mode | 0o400)
        elif mode == '-r':
            return "{0:#o}".format(st.st_mode & 0o377)
        elif mode == '+w':
            return "{0:#o}".format(st.st_mode | 0o200)
        elif mode == '-w':
            return "{0:#o}".format(st.st_mode & 0o577)
        elif mode == '+x':
            return "{0:#o}".format(st.st_mode | 0o111)
        elif mode == '-x':
            return "{0:#o}".format(st.st_mode & 0o666)
        else:
            return mode

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
            ui.getcomponent("Cmdline").restart("")
        else:
            if string == "":
                self.group = -1
            else:
                self.group = string
            filectrl.chown(ui.getcomponent("Filer").file.name, self.user, self.group)

class Copy(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if ui.getcomponent("Filer").dir.ismark():
            return "Copy mark files to:"
        elif self.src:
            return "Copy from {0} to:".format(self.src)
        elif self.src is None:
            return "Copy from:"
        else:
            return "Copy:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                return message.error("Copy error: Destination is not directory")
            filectrl.copy(filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.copy(self.src, path)

class CreateWorkspace(object):
    prompt = "Create workspace (title):"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        ui.getcomponent("Filer").create_workspace(title)

class Delete(object):
    @property
    def prompt(self):
        return "Delete:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        msg = path.replace(filer.dir.path, "")
        ret = message.confirm("Delete? ({0}):".format(msg), ["No", "Yes"])
        if ret == "Yes":
            filectrl.delete(path)

class Glob(object):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return "Glob pattern:"
        else:
            return "Glob pattern (default {0}):".format(self.default)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        filer = ui.getcomponent("Filer")
        if not self.default == "" and pattern == "":
            filer.dir.glob(self.default)
        else:
            if pattern == "":
                return
            Glob.default = pattern
            filer.dir.glob(pattern)

class GlobDir(object):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return "Glob dir pattern:"
        else:
            return "Glob dir pattern (default {0}):".format(self.default)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        filer = ui.getcomponent("Filer")
        if not self.default == "" and pattern == "":
            filer.dir.globdir(self.default)
        else:
            if pattern == "":
                return
            GlobDir.default = pattern
            filer.dir.globdir(pattern)

class Help(object):
    prompt = 'Help:'

    def complete(self, comp):
        return comp.comp_pyful_commands()

    def execute(self, cmd):
        ui.getcomponent("Help").show_command(cmd)

class Link(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if ui.getcomponent("Filer").dir.ismark():
            return "Link mark files to:"
        elif self.src:
            return "Link from `{0}' to:".format(self.src)
        elif self.src is None:
            return "Link from:"
        else:
            return "Link:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Error: Destination is not directory")
                return
            for f in filer.dir.get_mark_files():
                dst = os.path.join(path, util.unix_basename(f))
                filectrl.link(f, dst)
            filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.link(self.src, path)
            filer.workspace.all_reload()

class Mark(object):
    default = None

    @property
    def prompt(self):
        if self.default:
            return "Mark pattern (default {0}):".format(self.default.pattern)
        else:
            return "Mark pattern:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        filer = ui.getcomponent("Filer")
        if self.default and pattern == "":
            filer.dir.mark(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except re.error as e:
                return message.exception(e)
            self.__class__.default = reg
            filer.dir.mark(reg)

class Mask(object):
    default = None

    @property
    def prompt(self):
        if self.default:
            return "Mask pattern (default {0}):".format(self.default.pattern)
        else:
            return "Mask pattern:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        filer = ui.getcomponent("Filer")
        if self.default and pattern == "":
            filer.dir.mask(self.default)
        else:
            try:
                r = re.compile(pattern)
            except re.error as e:
                return message.exception(e)
            self.__class__.default = r
            filer.dir.mask(r)

class Menu(object):
    prompt = 'Menu name:'

    def complete(self, comp):
        return sorted([item for item in ui.getcomponent("Menu").items.keys()
                       if item.startswith(comp.parser.part[1])])

    def execute(self, name):
        ui.getcomponent("Menu").show(name)

class Mkdir(object):
    dirmode = 0o755
    prompt = "Make directory:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        filectrl.mkdir(path, self.dirmode)
        filer.workspace.all_reload()
        filer.dir.setcursor(filer.dir.get_index(util.unix_basename(path)))

class Move(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if ui.getcomponent("Filer").dir.ismark():
            return "Move mark files to:"
        elif self.src:
            return "Move from {0} to:".format(self.src)
        elif self.src is None:
            return "Move from:"
        else:
            return "Move:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Move error: Destination is not directory")
                return
            filectrl.move(filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.move(self.src, path)

class Newfile(object):
    filemode = 0o644
    prompt = "New file:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if os.path.exists(util.abspath(path)):
            return message.error("Error: file exists - {0}".format(path))
        filectrl.mknod(path, self.filemode)
        filer.workspace.all_reload()
        filer.dir.setcursor(filer.dir.get_index(path))

class OpenListfile(object):
    prompt = 'Open list file:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if os.path.exists(path):
            filer.dir.open_listfile(path)
        else:
            message.error('No such list file: ' + path)

class Rename(object):
    def __init__(self, path=None):
        filer = ui.getcomponent("Filer")
        if path is None:
            self.path = filer.file.name
        else:
            self.path = path

    @property
    def prompt(self):
        try:
            util.U(self.path)
            return "Rename: {0} ->".format(self.path)
        except UnicodeError:
            return "Rename invalid encoding to:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filectrl.rename(self.path, path)
        ui.getcomponent("Filer").workspace.all_reload()

class Replace(object):
    default = []
    pattern = None

    @property
    def prompt(self):
        if self.pattern is None and self.default:
            return "Replace regexp (default {0} -> {1}):".format(self.default[0].pattern, self.default[1])
        elif self.pattern is None:
            return "Replace pattern:"
        else:
            return "Replace regexp {0} with:".format(self.pattern.pattern)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern):
        filer = ui.getcomponent("Filer")
        if not pattern and not self.pattern and self.default:
            filectrl.replace(self.default[0], self.default[1])
            filer.dir.mark_clear()
            filer.workspace.all_reload()
        elif self.pattern is None:
            try:
                self.pattern = re.compile(util.U(pattern))
            except re.error as e:
                return message.exception(e)
            ui.getcomponent("Cmdline").restart("")
        else:
            filectrl.replace(self.pattern, pattern)
            Replace.default[:] = []
            Replace.default.append(self.pattern)
            Replace.default.append(pattern)
            filer.dir.mark_clear()
            filer.workspace.all_reload()

class Symlink(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            return "Symlink mark files to:"
        elif self.src:
            return "Symlink from `{0}' to:".format(self.src)
        elif self.src is None:
            return "Symlink from:"
        else:
            return "Symlink:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            if not os.path.exists(path):
                return message.error("{0} - {1}".format(os.strerror(errno.ENOENT), path))
            elif not os.path.isdir(path):
                return message.error("{0} - {1}".format(os.strerror(errno.ENOTDIR), path))
            for f in filer.dir.get_mark_files():
                dst = os.path.join(path, os.path.basename(f))
                filectrl.symlink(os.path.abspath(f), dst)
            filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.symlink(self.src, path)
            filer.workspace.all_reload()

class TrashBox(object):
    prompt = "Trashbox:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        trashbox = os.path.expanduser(Pyful.environs['TRASHBOX'])
        msg = path.replace(filer.dir.path, "")
        ret = message.confirm("Move `{0}' to trashbox? ".format(msg), ["No", "Yes"])
        if ret == "Yes":
            filectrl.move(path, trashbox)
            filer.workspace.all_reload()

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
            return "Utime year: {0} ->".format(self.timesec[0])
        elif len(self.sttime) == 1:
            return "Utime month: {0} ->".format(self.timesec[1])
        elif len(self.sttime) == 2:
            return "Utime day: {0} ->".format(self.timesec[2])
        elif len(self.sttime) == 3:
            return "Utime hour: {0} ->".format(self.timesec[3])
        elif len(self.sttime) == 4:
            return "Utime min: {0} ->".format(self.timesec[4])
        elif len(self.sttime) == 5:
            return "Utime sec: {0} ->".format(self.timesec[5])

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
        cmdline = ui.getcomponent("Cmdline")
        if not self.path:
            if os.path.exists(st):
                self.path = st
                self.timesec = time.localtime(os.stat(self.path).st_mtime)
                cmdline.restart("")
            else:
                return message.error("{0} doesn't exist.".format(st))

        elif len(self.sttime) == 0:
            if st == "":
                self.sttime.append(self.timesec[0])
            else:
                self.sttime.append(int(st))
            cmdline.restart("")
        elif len(self.sttime) == 1:
            if st == "":
                self.sttime.append(self.timesec[1])
            elif 0 < int(st) <= 12:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[1])
            cmdline.restart("")
        elif len(self.sttime) == 2:
            if st == "":
                self.sttime.append(self.timesec[2])
            elif 0 < int(st) <= 31:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[2])
            cmdline.restart("")
        elif len(self.sttime) == 3:
            if st == "":
                self.sttime.append(self.timesec[3])
            elif 0 <= int(st) <= 23:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[3])
            cmdline.restart("")
        elif len(self.sttime) == 4:
            if st == "":
                self.sttime.append(self.timesec[4])
            elif 0 <= int(st) <= 59:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[4])
            cmdline.restart("")
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
                message.exception(e)
            ui.getcomponent("Filer").workspace.all_reload()

class Tar(object):
    def __init__(self, tarmode, each=False):
        self.src = None
        self.wrap = None
        self.tarmode = tarmode
        self.each = each

    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                return 'Mark files wrap is:'
            else:
                if self.each:
                    return 'Mark files {0} each to:'.format(self.tarmode)
                else:
                    return 'Mark files {0} to:'.format(self.tarmode)
        elif self.src is None:
            return '{0} from:'.format(self.tarmode)
        else:
            return '{0} from {1} to:'.format(self.tarmode, self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        cmdline = ui.getcomponent("Cmdline")
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    cmdline.restart(filer.workspace.nextdir.path)
                else:
                    ext = filectrl.TarThread.tarexts[self.tarmode]
                    tarpath = os.path.join(filer.workspace.nextdir.path, self.wrap + ext)
                    cmdline.restart(tarpath, -len(ext))
            else:
                if self.each:
                    filectrl.tareach(filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                else:
                    filectrl.tar(filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = filectrl.TarThread.tarexts[self.tarmode]
            tarpath = os.path.join(filer.workspace.nextdir.path, self.src + ext)
            cmdline.restart(tarpath, -len(ext))
        else:
            filectrl.tar(self.src, path, self.tarmode)
            filer.workspace.all_reload()

class UnTar(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            return 'Mark files untar to:'
        elif self.src is None:
            return 'Untar from:'
        else:
            return 'Untar from {0} to:'.format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            filectrl.untar(filer.dir.get_mark_files(), path)
            filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.untar(self.src, path)
            filer.workspace.all_reload()

class WebSearch(object):
    def __init__(self, engine='Google'):
        self.engine = engine

    @property
    def prompt(self):
        return '{0} search:'.format(self.engine)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, word):
        import webbrowser
        if self.engine == 'Google':
            word = word.replace(' ', '+')
            search = 'http://www.google.com/search?&q={0}'.format(word)
        else:
            pass
        try:
            webbrowser.open(search, new=2)
        except Exception as e:
            message.exception(e)

class Zip(object):
    def __init__(self, each=False):
        self.src = None
        self.wrap = None
        self.each = each

    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark() or self.each:
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
            return 'Zip from {0} to:'.format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        cmdline = ui.getcomponent("Cmdline")
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    cmdline.restart(filer.workspace.nextdir.path)
                else:
                    ext = '.zip'
                    zippath = os.path.join(filer.workspace.nextdir.path, self.wrap + ext)
                    cmdline.restart(zippath, -len(ext))
            else:
                if self.each:
                    filectrl.zipeach(filer.dir.get_mark_files(), path, self.wrap)
                else:
                    filectrl.zip(filer.dir.get_mark_files(), path, self.wrap)
                filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = '.zip'
            zippath = os.path.join(filer.workspace.nextdir.path, self.src + ext)
            cmdline.restart(zippath, -len(ext))
        else:
            filectrl.zip(self.src, path)
            filer.workspace.all_reload()

class UnZip(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            return 'Mark files unzip to:'
        elif self.src is None:
            return 'Unzip from:'
        else:
            return 'Unzip from {0} to:'.format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        filer = ui.getcomponent("Filer")
        if filer.dir.ismark():
            filectrl.unzip(filer.dir.get_mark_files(), path)
            filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ui.getcomponent("Cmdline").restart(filer.workspace.nextdir.path)
        else:
            filectrl.unzip(self.src, path)
            filer.workspace.all_reload()

class ZoomInfoBox(object):
    prompt = 'Zoom infobox:'

    def complete(self, comp):
        return [str(x*10) for x in range(-10, 11) if str(x*10).startswith(comp.parser.part[1])]

    def execute(self, zoom):
        try:
            zoom = int(zoom)
            ui.zoom_infobox(zoom)
        except ValueError as e:
            message.exception(e)
