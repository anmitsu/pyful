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

import os
import re
import time

from pyful import Pyful
from pyful import filectrl
from pyful import process
from pyful import ui
from pyful import util
from pyful import message
from pyful.cmdline import Cmdline
from pyful.filer import Filer
from pyful.menu import Menu

_cmdline = Cmdline()
_filer = Filer()
_menu = Menu()

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
            message.error("Undefined command `%s'" % cmd)

class ChangeWorkspaceTitle(object):
    prompt = 'Change workspace title:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        _filer.workspace.chtitle(title)

class Chdir(object):
    prompt = 'Chdir to:'

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        _filer.dir.chdir(path)

class Chmod(object):
    @property
    def prompt(self):
        if _filer.dir.ismark():
            return "Chmod mark files:"
        else:
            mode = "%o" % _filer.file.stat.st_mode
            return "Chmod (%s - %s):" % (_filer.file.name, mode)

    def complete(self, comp):
        pass

    def execute(self, mode):
        if _filer.dir.ismark():
            for f in _filer.dir.get_mark_files():
                filectrl.chmod(f, mode)
        else:
            filectrl.chmod(_filer.file.name, mode)
        _filer.workspace.all_reload()

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
            _cmdline.restart("")
        else:
            if string == "":
                self.group = -1
            else:
                self.group = string
            filectrl.chown(_filer.file.name, self.user, self.group)

class Copy(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
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
        if _filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Copy error: Destination is not directory")
                return
            filectrl.copy(_filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.copy(self.src, path)

class CreateWorkspace(object):
    prompt = "Create workspace (title):"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title):
        _filer.create_workspace(title)

class Delete(object):
    @property
    def prompt(self):
        return "Delete:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        msg = path.replace(_filer.dir.path, "")
        ret = message.confirm("Delete? (%s):"%msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return
        filectrl.delete(path)
        _filer.workspace.all_reload()

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
            _filer.dir.glob(self.default)
        else:
            if pattern == "":
                return
            Glob.default = pattern
            _filer.dir.glob(pattern)

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
            _filer.dir.globdir(self.default)
        else:
            if pattern == "":
                return
            GlobDir.default = pattern
            _filer.dir.globdir(pattern)

class Link(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
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
        if _filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Error: Destination is not directory")
                return
            for f in _filer.dir.get_mark_files():
                dst = os.path.join(path, util.unix_basename(f))
                filectrl.link(f, dst)
            _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.link(self.src, path)
            _filer.workspace.all_reload()

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
            _filer.dir.mark(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except Exception as e:
                message.error("Regexp error: " + str(e))
                return
            self.__class__.default = reg
            _filer.dir.mark(reg)

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
            _filer.dir.mask(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except:
                return message.error("Argument error: Can't complile `%s'" % pattern)
            self.__class__.default = reg
            _filer.dir.mask(reg)

class Menu(object):
    prompt = 'Menu name:'

    def complete(self, comp):
        return list(_menu.items.keys())

    def execute(self, name):
        _menu.show(name)

class Mkdir(object):
    dirmode = 0o755
    prompt = "Make directory:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        filectrl.mkdir(path, self.dirmode)
        _filer.workspace.all_reload()
        _filer.dir.setcursor(_filer.dir.get_index(util.unix_basename(path)))

class Move(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
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
        if _filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Move error: Destination is not directory")
                return
            filectrl.move(_filer.dir.get_mark_files(), path)
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.move(self.src, path)

class Newfile(object):
    filemode = 0o644
    prompt = "New file:"

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(util.abspath(path)):
            message.error("Error: file exists - %s" % path)
            return
        filectrl.mknod(path, self.filemode)
        _filer.workspace.all_reload()
        _filer.dir.setcursor(_filer.dir.get_index(path))

class OpenListfile(object):
    prompt = 'Open list file:'

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if os.path.exists(path):
            _filer.dir.open_listfile(path)
        else:
            message.error('No such list file: ' + path)

class Rename(object):
    def __init__(self, path=None):
        if path is None:
            self.path = _filer.file.name
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
            message.error("Error: File exist - %s" % path)
            return

        try:
            os.renames(self.path, path)
            message.puts("Renamed: %s -> %s" % (self.path, path))
        except Exception as e:
            message.exception(e)
        _filer.workspace.all_reload()

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
            _filer.dir.mark_clear()
            _filer.workspace.all_reload()
        elif self.pattern is None:
            try:
                self.pattern = re.compile(util.unistr(pattern))
            except Exception:
                return message.error("Argument error: Can't complile `%s'" % pattern)
            _cmdline.restart("")
        else:
            filectrl.replace(self.pattern, pattern)
            Replace.default[:] = []
            Replace.default.append(self.pattern)
            Replace.default.append(pattern)
            _filer.dir.mark_clear()
            _filer.workspace.all_reload()

class Symlink(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
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
        if _filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                message.error("Symlink error: Destination is not directory")
                return
            for f in _filer.dir.get_mark_files():
                dst = os.path.join(path, os.path.basename(f))
                filectrl.symlink(f, dst)
            _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.symlink(self.src, path)
            _filer.workspace.all_reload()

class TrashBox(object):
    prompt = "Trashbox:"

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path):
        trashbox = os.path.expanduser(Pyful.environs['TRASHBOX'])
        msg = path.replace(_filer.dir.path, "")
        ret = message.confirm("Move `%s' to trashbox? " % msg, ["No", "Yes"])
        if ret == "No" or ret is None:
            return

        filectrl.move(path, trashbox)
        _filer.workspace.all_reload()

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
                _cmdline.restart("")
            else:
                return message.error("%s doesn't exist." % st)

        elif len(self.sttime) == 0:
            if st == "":
                self.sttime.append(self.timesec[0])
            else:
                self.sttime.append(int(st))
            _cmdline.restart("")
        elif len(self.sttime) == 1:
            if st == "":
                self.sttime.append(self.timesec[1])
            elif 0 < int(st) <= 12:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[1])
            _cmdline.restart("")
        elif len(self.sttime) == 2:
            if st == "":
                self.sttime.append(self.timesec[2])
            elif 0 < int(st) <= 31:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[2])
            _cmdline.restart("")
        elif len(self.sttime) == 3:
            if st == "":
                self.sttime.append(self.timesec[3])
            elif 0 <= int(st) <= 23:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[3])
            _cmdline.restart("")
        elif len(self.sttime) == 4:
            if st == "":
                self.sttime.append(self.timesec[4])
            elif 0 <= int(st) <= 59:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[4])
            _cmdline.restart("")
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
                message.error(str(e))
            _filer.workspace.all_reload()

class Tar(object):
    def __init__(self, tarmode, each=False):
        self.src = None
        self.wrap = None
        self.tarmode = tarmode
        self.each = each

    @property
    def prompt(self):
        if _filer.dir.ismark() or self.each:
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
        if _filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    _cmdline.restart(_filer.workspace.nextdir.path)
                else:
                    ext = filectrl.TarThread.tarexts[self.tarmode]
                    tarpath = os.path.join(_filer.workspace.nextdir.path, self.wrap + ext)
                    _cmdline.restart(tarpath, -len(ext))
            else:
                if self.each:
                    filectrl.tareach(_filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                else:
                    filectrl.tar(_filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = filectrl.TarThread.tarexts[self.tarmode]
            tarpath = os.path.join(_filer.workspace.nextdir.path, self.src + ext)
            _cmdline.restart(tarpath, -len(ext))
        else:
            filectrl.tar(self.src, path, self.tarmode)
            _filer.workspace.all_reload()

class UnTar(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
            return 'Mark files untar to:'
        elif self.src is None:
            return 'Untar from:'
        else:
            return 'Untar from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if _filer.dir.ismark():
            filectrl.untar(_filer.dir.get_mark_files(), path)
            _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.untar(self.src, path)
            _filer.workspace.all_reload()

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
            message.exception(e)

class Zip(object):
    def __init__(self, each=False):
        self.src = None
        self.wrap = None
        self.each = each

    @property
    def prompt(self):
        if _filer.dir.ismark() or self.each:
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
        if _filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    _cmdline.restart(_filer.workspace.nextdir.path)
                else:
                    ext = '.zip'
                    zippath = os.path.join(_filer.workspace.nextdir.path, self.wrap + ext)
                    _cmdline.restart(zippath, -len(ext))
            else:
                if self.each:
                    filectrl.zipeach(_filer.dir.get_mark_files(), path, self.wrap)
                else:
                    filectrl.zip(_filer.dir.get_mark_files(), path, self.wrap)
                _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            ext = '.zip'
            zippath = os.path.join(_filer.workspace.nextdir.path, self.src + ext)
            _cmdline.restart(zippath, -len(ext))
        else:
            filectrl.zip(self.src, path)
            _filer.workspace.all_reload()

class UnZip(object):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if _filer.dir.ismark():
            return 'Mark files unzip to:'
        elif self.src is None:
            return 'Unzip from:'
        else:
            return 'Unzip from %s to:' % self.src

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path):
        if _filer.dir.ismark():
            filectrl.unzip(_filer.dir.get_mark_files(), path)
            _filer.workspace.all_reload()
        elif self.src is None:
            self.src = path
            _cmdline.restart(_filer.workspace.nextdir.path)
        else:
            filectrl.unzip(self.src, path)
            _filer.workspace.all_reload()

class ZoomInfoBox(object):
    prompt = 'Zoom infobox:'

    def complete(self, comp):
        return [str(x*10) for x in range(-10, 11)]

    def execute(self, zoom):
        try:
            zoom = int(zoom)
            ui.zoom_infobox(zoom)
        except ValueError as e:
            message.exception(e)
