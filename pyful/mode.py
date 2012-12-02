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

from pyful import filectrl
from pyful import look
from pyful import message
from pyful import process
from pyful import util
from pyful import widget
from pyful import widgets

from pyful.widget.listbox import ListBox, Entry

class ActionBox(ListBox):
    def __init__(self):
        ListBox.__init__(self, "ActionBox")
        self.selected = None

    def select_action(self):
        self.selected = self.cursor_entry().text
        self.hide()

    def run(self, actions):
        if not actions:
            return
        self.selected = None
        self.show([Entry(a) for a in actions])

        def _draw():
            widgets.filer.draw()
            widgets.cmdline.draw()
            self.draw()
        ui = widget.ui.UI(_draw, self.input)
        while self.active:
            ui.run()
        return self.selected

class Mode(object):
    actionbox = ActionBox()
    actions = []
    prompt = ""

    def select_action(self):
        return self.actionbox.run(self.actions)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, cmdstring, action):
        pass

class Shell(Mode):
    prompt = " $ "
    actions = ["Run background", "Run external terminal", "Run quickly",]

    def complete(self, comp):
        return comp.complete()

    def execute(self, cmd, action):
        if action == self.actions[0]:
            cmd += "%&"
        elif action == self.actions[1]:
            cmd += "%T"
        elif action == self.actions[2]:
            cmd += "%q"
        process.spawn(cmd, expandmacro=False)

class Eval(Mode):
    prompt = " Eval: "
    actions = ["Run quickly",]

    def complete(self, comp):
        return comp.comp_python_builtin_functions()

    def execute(self, cmd, action):
        if action == self.actions[0]:
            cmd += "%q"
        process.python(cmd)

class Mx(Mode):
    prompt = " M-x "
    actions = ["Show command help",]

    def complete(self, comp):
        return comp.comp_pyful_commands()

    def execute(self, cmd, action):
        if action == self.actions[0]:
            widgets.help.show_command(cmd)
            return (cmd, -1)
        else:
            from pyful.command import commands
            try:
                commands[cmd]()
            except KeyError:
                message.error("Undefined command `{0}'".format(cmd))

class ChangeLooks(Mode):
    prompt = " Change looks: "

    def complete(self, comp):
        return sorted([l for l in look.looks.keys()
                       if l.startswith(comp.parser.part[1])])

    def execute(self, name, action):
        if name in look.looks:
            look.Look.mylook = name
            look.init_colors()
            widget.refresh_all_widgets()
        else:
            message.error("`{0}' looks doesn't exist".format(name))

class ChangeWorkspaceTitle(Mode):
    prompt = " Change workspace title: "

    def complete(self, comp):
        return [ws.title for ws in widgets.filer.workspaces
                if ws.title.startswith(comp.parser.part[1])]

    def execute(self, title, action):
        widgets.filer.workspace.chtitle(title)

class Chdir(Mode):
    prompt = " Chdir to: "

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path, action):
        widgets.filer.dir.chdir(path)

class Chmod(Mode):
    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark():
            return " Chmod mark files: "
        else:
            return " Chmod ({0} - {1:#o}): ".format(filer.file.name, filer.file.stat.st_mode)

    def complete(self, comp):
        symbols = ["+r", "-r", "+w", "-w", "+x", "-x"]
        return sorted([symb for symb in symbols if symb.startswith(comp.parser.part[1])])

    def execute(self, mode, action):
        filer = widgets.filer
        if filer.dir.ismark():
            for f in filer.dir.get_mark_files():
                mode = self._getmode(os.stat(f), mode)
                filectrl.chmod(f, mode)
        else:
            mode = self._getmode(filer.file.stat, mode)
            filectrl.chmod(filer.file.name, mode)
        filer.workspace.all_reload()

    def _getmode(self, st, mode):
        if mode == "+r":
            return "{0:#o}".format(st.st_mode | 0o400)
        elif mode == "-r":
            return "{0:#o}".format(st.st_mode & 0o377)
        elif mode == "+w":
            return "{0:#o}".format(st.st_mode | 0o200)
        elif mode == "-w":
            return "{0:#o}".format(st.st_mode & 0o577)
        elif mode == "+x":
            return "{0:#o}".format(st.st_mode | 0o111)
        elif mode == "-x":
            return "{0:#o}".format(st.st_mode & 0o666)
        else:
            return mode

class Chown(Mode):
    def __init__(self):
        self.user = None
        self.group = None

    @property
    def prompt(self):
        if self.user is None:
            return " User: "
        elif self.group is None:
            return " Group: "
        else:
            return " Chown: "

    def complete(self, comp):
        if self.user is None:
            return comp.comp_username()
        elif self.group is None:
            return comp.comp_groupname()

    def execute(self, string, action):
        if self.user is None:
            if string == "":
                self.user = -1
            else:
                self.user = string
            return ("", 0)
        else:
            if string == "":
                self.group = -1
            else:
                self.group = string
            filectrl.chown(widgets.filer.file.name, self.user, self.group)

class Copy(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if widgets.filer.dir.ismark():
            return " Copy mark files to: "
        elif self.src:
            return " Copy from {0} to: ".format(self.src)
        elif self.src is None:
            return " Copy from: "
        else:
            return " Copy: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark():
            filectrl.copy(filer.dir.get_mark_files(), path)
        elif self.src is None:
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.copy(self.src, path)

class CreateWorkspace(Mode):
    prompt = " Create workspace (title): "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, title, action):
        widgets.filer.create_workspace(title)

class Delete(Mode):
    @property
    def prompt(self):
        return " Delete: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        if not path:
            return
        filer = widgets.filer
        msg = path.replace(filer.dir.path, "")
        ret = message.confirm("Delete? ({0}):".format(msg), ["No", "Yes"])
        if ret == "Yes":
            filectrl.delete(path)

class Glob(Mode):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return " Glob pattern: "
        else:
            return " Glob pattern (default {0}): ".format(self.default)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern, action):
        filer = widgets.filer
        if not self.default == "" and pattern == "":
            filer.dir.glob(self.default)
        else:
            if pattern == "":
                return
            Glob.default = pattern
            filer.dir.glob(pattern)

class GlobDir(Mode):
    default = ""

    @property
    def prompt(self):
        if self.default == "":
            return " Glob dir pattern: "
        else:
            return " Glob dir pattern (default {0}): ".format(self.default)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern, action):
        filer = widgets.filer
        if not self.default == "" and pattern == "":
            filer.dir.globdir(self.default)
        else:
            if pattern == "":
                return
            GlobDir.default = pattern
            filer.dir.globdir(pattern)

class Help(Mode):
    prompt = " Help: "

    def complete(self, comp):
        return comp.comp_pyful_commands()

    def execute(self, cmd, action):
        widgets.help.show_command(cmd)

class Link(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if widgets.filer.dir.ismark():
            return " Link mark files to: "
        elif self.src:
            return " Link from `{0}' to: ".format(self.src)
        elif self.src is None:
            return " Link from: "
        else:
            return " Link: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark():
            if not path.endswith(os.sep) and not os.path.isdir(path):
                return message.error("{0} - {1}".format(os.strerror(errno.ENOTDIR), path))
            for f in filer.dir.get_mark_files():
                dst = os.path.join(path, util.unix_basename(f))
                filectrl.link(f, dst)
            filer.workspace.all_reload()
        elif self.src is None:
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.link(self.src, path)
            filer.workspace.all_reload()

class Mark(Mode):
    actions = [
        "Mark image files", "Mark music files", "Mark video files",
        "Mark archive files", "Mark source files"]
    filters = {
        "image": r"\.(jpe?g|gif|png|bmp|tiff|jp2|j2c|svg|eps)$",
        "music": r"\.(ogg|mp3|flac|ape|tta|tak|mid|wma|wav)$",
        "video": r"\.(avi|mkv|mp4|mpe?g|wmv|asf|rm|ram|ra)$",
        "archive": r"\.(zip|rar|lzh|cab|tar|7z|gz|bz2|xz|taz|tgz|tbz|txz|yz2)$",
        "source": r"\.(py|rb|hs|el|js|lua|java|c|cc|cpp|cs|pl|php)$",
        }
    default = None

    @property
    def prompt(self):
        if self.default:
            return " Mark pattern (default {0}): ".format(self.default.pattern)
        else:
            return " Mark pattern: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern, action):
        if action == self.actions[0]:
            return (self.filters["image"], -1)
        elif action == self.actions[1]:
            return (self.filters["music"], -1)
        elif action == self.actions[2]:
            return (self.filters["video"], -1)
        elif action == self.actions[3]:
            return (self.filters["archive"], -1)
        elif action == self.actions[4]:
            return (self.filters["source"], -1)

        filer = widgets.filer
        if self.default and pattern == "":
            filer.dir.mark(self.default)
        else:
            try:
                reg = re.compile(pattern)
            except re.error as e:
                return message.exception(e)
            self.__class__.default = reg
            filer.dir.mark(reg)

class Mask(Mode):
    actions = [
        "Mask image files", "Mask music files", "Mask video files",
        "Mask archive files", "Mask source files"]
    filters = {
        "image": r"\.(jpe?g|gif|png|bmp|tiff|jp2|j2c|svg|eps)$",
        "music": r"\.(ogg|mp3|flac|ape|tta|tak|mid|wma|wav)$",
        "video": r"\.(avi|mkv|mp4|mpe?g|wmv|asf|rm|ram|ra)$",
        "archive": r"\.(zip|rar|lzh|cab|tar|7z|gz|bz2|xz|taz|tgz|tbz|txz|yz2)$",
        "source": r"\.(py|rb|hs|el|js|lua|java|c|cc|cpp|cs|pl|php)$",
        }
    default = None

    @property
    def prompt(self):
        if self.default:
            return " Mask pattern (default {0}): ".format(self.default.pattern)
        else:
            return " Mask pattern: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, pattern, action):
        if action == self.actions[0]:
            return (self.filters["image"], -1)
        elif action == self.actions[1]:
            return (self.filters["music"], -1)
        elif action == self.actions[2]:
            return (self.filters["video"], -1)
        elif action == self.actions[3]:
            return (self.filters["archive"], -1)
        elif action == self.actions[4]:
            return (self.filters["source"], -1)

        filer = widgets.filer
        if self.default and pattern == "":
            filer.dir.mask(self.default)
        else:
            try:
                r = re.compile(pattern)
            except re.error as e:
                return message.exception(e)
            self.__class__.default = r
            filer.dir.mask(r)

class Menu(Mode):
    prompt = " Menu name: "

    def complete(self, comp):
        return sorted([item for item in widgets.menu.items.keys()
                       if item.startswith(comp.parser.part[1])])

    def execute(self, name, action):
        widgets.menu.show(name)

class Mkdir(Mode):
    dirmode = 0o755
    prompt = " Make directory: "

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path, action):
        filer = widgets.filer
        filectrl.mkdir(path, self.dirmode)
        filer.workspace.all_reload()
        filer.dir.setcursor(filer.dir.get_index(util.unix_basename(path)))

class Move(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        if widgets.filer.dir.ismark():
            return " Move mark files to: "
        elif self.src:
            return " Move from {0} to: ".format(self.src)
        elif self.src is None:
            return " Move from: "
        else:
            return " Move: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark():
            filectrl.move(filer.dir.get_mark_files(), path)
        elif self.src is None:
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.move(self.src, path)

class Newfile(Mode):
    filemode = 0o644
    prompt = " New file: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        filectrl.mknod(path, self.filemode)
        filer.workspace.all_reload()
        filer.dir.setcursor(filer.dir.get_index(path))

class OpenListfile(Mode):
    prompt = " Open list file: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if os.path.exists(path):
            filer.dir.open_listfile(path)
        else:
            message.error("No such list file: " + path)

class Rename(Mode):
    def __init__(self, path=None):
        filer = widgets.filer
        if path is None:
            self.path = filer.file.name
        else:
            self.path = path

    @property
    def prompt(self):
        return " Rename: {0} -> ".format(self.path)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filectrl.rename(self.path, path)
        widgets.filer.workspace.all_reload()

class Replace(Mode):
    form = "emacs"
    default = []
    pattern = None
    actions = ["Replace on form of `emacs'", "Replace on form of `vim'",]

    def _get_emacs_prompt(self):
        if self.pattern is None and self.default:
            return " Replace regexp (default {0} -> {1}): ".format(self.default[0].pattern, self.default[1])
        elif self.pattern is None:
            return " Replace pattern: "
        else:
            return " Replace regexp {0} with: ".format(self.pattern.pattern)

    def _get_vim_prompt(self):
        return " :%s/"

    @property
    def prompt(self):
        if self.form == "emacs":
            return self._get_emacs_prompt()
        elif self.form == "vim":
            return self._get_vim_prompt()
        else:
            return self._get_emacs_prompt()

    def select_action(self):
        if self.pattern is None:
            return self.actionbox.run(self.actions)

    def complete(self, comp):
        return comp.comp_files()

    def _run_emacs_replace(self, pattern):
        filer = widgets.filer
        if not pattern and not self.pattern and self.default:
            filectrl.replace(self.default[0], self.default[1])
            filer.dir.mark_clear()
            filer.workspace.all_reload()
        elif self.pattern is None:
            try:
                self.pattern = re.compile(util.U(pattern))
            except re.error as e:
                return message.exception(e)
            return ("", 0)
        else:
            filectrl.replace(self.pattern, pattern)
            Replace.default[:] = []
            Replace.default.append(self.pattern)
            Replace.default.append(pattern)
            filer.workspace.all_reload()

    def _run_vim_replace(self, pattern):
        filer = widgets.filer
        patterns = re.split(r"(?<!\\)/", pattern)
        if len(patterns) > 1:
            pattern = util.U(patterns[0])
            repl = patterns[1]
        else:
            pattern = util.U(pattern)
            repl = ""
        pattern = re.sub(r"\\/", "/", pattern)
        repl = re.sub(r"\\/", "/", repl)
        try:
            reg = re.compile(pattern)
        except re.error as e:
            return message.exception(e)
        filectrl.replace(reg, repl)
        filer.workspace.all_reload()

    def execute(self, pattern, action):
        if action == self.actions[0]:
            self.form = "emacs"
            return (pattern, -1)
        elif action == self.actions[1]:
            self.form = "vim"
            return (pattern, -1)

        if self.form == "emacs":
            self._run_emacs_replace(pattern)
        elif self.form == "vim":
            self._run_vim_replace(pattern)
        else:
            self._run_emacs_replace(pattern)

class Symlink(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark():
            return " Symlink mark files to: "
        elif self.src:
            return " Symlink from `{0}' to: ".format(self.src)
        elif self.src is None:
            return " Symlink from: "
        else:
            return " Symlink: "

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
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
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.symlink(self.src, path)
            filer.workspace.all_reload()

class TrashBox(Mode):
    path = os.path.join(os.getenv("HOME"), ".pyful", "trashbox")
    prompt = " Trashbox: "

    def complete(self, comp):
        return comp.comp_dirs()

    def execute(self, path, action):
        filer = widgets.filer
        trashbox = os.path.expanduser(self.path)
        msg = path.replace(filer.dir.path, "")
        ret = message.confirm("Move `{0}' to trashbox? ".format(msg), ["No", "Yes"])
        if ret == "Yes":
            filectrl.move(path, trashbox)
            filer.workspace.all_reload()

class Utime(Mode):
    def __init__(self):
        self.sttime = []
        self.path = None
        self.timesec = None

    @property
    def prompt(self):
        if not self.path:
            return " Utime path: "
        elif len(self.sttime) == 0:
            return " Utime year: {0} -> ".format(self.timesec[0])
        elif len(self.sttime) == 1:
            return " Utime month: {0} -> ".format(self.timesec[1])
        elif len(self.sttime) == 2:
            return " Utime day: {0} -> ".format(self.timesec[2])
        elif len(self.sttime) == 3:
            return " Utime hour: {0} -> ".format(self.timesec[3])
        elif len(self.sttime) == 4:
            return " Utime min: {0} -> ".format(self.timesec[4])
        elif len(self.sttime) == 5:
            return " Utime sec: {0} -> ".format(self.timesec[5])

    def complete(self, comp):
        if not self.path:
            return comp.comp_files()
        elif len(self.sttime) == 0:
            return [str(i) for i in range(1970-68, 1970+69)]
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

    def execute(self, st, action):
        if not self.path:
            if os.path.exists(st):
                self.path = st
                self.timesec = time.localtime(os.stat(self.path).st_mtime)
                return ("", 0)
            else:
                return message.error("{0} doesn't exist.".format(st))

        elif len(self.sttime) == 0:
            if st == "":
                self.sttime.append(self.timesec[0])
            else:
                self.sttime.append(int(st))
            return ("", 0)
        elif len(self.sttime) == 1:
            if st == "":
                self.sttime.append(self.timesec[1])
            elif 0 < int(st) <= 12:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[1])
            return ("", 0)
        elif len(self.sttime) == 2:
            if st == "":
                self.sttime.append(self.timesec[2])
            elif 0 < int(st) <= 31:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[2])
            return ("", 0)
        elif len(self.sttime) == 3:
            if st == "":
                self.sttime.append(self.timesec[3])
            elif 0 <= int(st) <= 23:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[3])
            return ("", 0)
        elif len(self.sttime) == 4:
            if st == "":
                self.sttime.append(self.timesec[4])
            elif 0 <= int(st) <= 59:
                self.sttime.append(int(st))
            else:
                self.sttime.append(self.timesec[4])
            return ("", 0)
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
            widgets.filer.workspace.all_reload()

class Tar(Mode):
    def __init__(self, tarmode, each=False):
        self.src = None
        self.wrap = None
        self.tarmode = tarmode
        self.each = each

    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                return " Mark files wrap is: "
            else:
                if self.each:
                    return " Mark files {0} each to: ".format(self.tarmode)
                else:
                    return " Mark files {0} to: ".format(self.tarmode)
        elif self.src is None:
            return " {0} from: ".format(self.tarmode)
        else:
            return " {0} from {1} to: ".format(self.tarmode, self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    return (filer.workspace.nextdir.path, -1)
                else:
                    ext = filectrl.TarThread.tarexts[self.tarmode]
                    tarpath = os.path.join(filer.workspace.nextdir.path, self.wrap + ext)
                    return (tarpath, -len(ext)-1)
            else:
                if self.each:
                    filectrl.tareach(filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                else:
                    filectrl.tar(filer.dir.get_mark_files(), path, self.tarmode, self.wrap)
                filer.workspace.all_reload()
        elif self.src is None:
            if not path:
                return
            self.src = path
            ext = filectrl.TarThread.tarexts[self.tarmode]
            tarpath = os.path.join(filer.workspace.nextdir.path, self.src + ext)
            return (tarpath, -len(ext)-1)
        else:
            filectrl.tar(self.src, path, self.tarmode)
            filer.workspace.all_reload()

class UnTar(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark():
            return " Mark files untar to: "
        elif self.src is None:
            return " Untar from: "
        else:
            return " Untar from {0} to: ".format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark():
            filectrl.untar(filer.dir.get_mark_files(), path)
            filer.workspace.all_reload()
        elif self.src is None:
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.untar(self.src, path)
            filer.workspace.all_reload()

class WebSearch(Mode):
    def __init__(self, engine="Google"):
        self.engine = engine

    @property
    def prompt(self):
        return " {0} search: ".format(self.engine)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, word, action):
        import webbrowser
        if self.engine == "Google":
            word = word.replace(" ", "+")
            search = "http://www.google.com/search?&q={0}".format(word)
        else:
            pass
        try:
            webbrowser.open(search, new=2)
        except Exception as e:
            message.exception(e)

class Zip(Mode):
    def __init__(self, each=False):
        self.src = None
        self.wrap = None
        self.each = each

    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                return " Mark files wrap is: "
            else:
                if self.each:
                    return " Mark files zip each to: "
                else:
                    return " Mark files zip to: "
        elif self.src is None:
            return " Zip from: "
        else:
            return " Zip from {0} to: ".format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark() or self.each:
            if self.wrap is None:
                self.wrap = path
                if self.each:
                    return (filer.workspace.nextdir.path, -1)
                else:
                    ext = ".zip"
                    zippath = os.path.join(filer.workspace.nextdir.path, self.wrap + ext)
                    return (zippath, -len(ext)-1)
            else:
                if self.each:
                    filectrl.zipeach(filer.dir.get_mark_files(), path, self.wrap)
                else:
                    filectrl.zip(filer.dir.get_mark_files(), path, self.wrap)
                filer.workspace.all_reload()
        elif self.src is None:
            if not path:
                return
            self.src = path
            ext = ".zip"
            zippath = os.path.join(filer.workspace.nextdir.path, self.src + ext)
            return (zippath, -len(ext)-1)
        else:
            filectrl.zip(self.src, path)
            filer.workspace.all_reload()

class UnZip(Mode):
    def __init__(self):
        self.src = None

    @property
    def prompt(self):
        filer = widgets.filer
        if filer.dir.ismark():
            return " Mark files unzip to: "
        elif self.src is None:
            return " Unzip from: "
        else:
            return " Unzip from {0} to: ".format(self.src)

    def complete(self, comp):
        return comp.comp_files()

    def execute(self, path, action):
        filer = widgets.filer
        if filer.dir.ismark():
            filectrl.unzip(filer.dir.get_mark_files(), path)
            filer.workspace.all_reload()
        elif self.src is None:
            if not path:
                return
            self.src = path
            return (filer.workspace.nextdir.path, -1)
        else:
            filectrl.unzip(self.src, path)
            filer.workspace.all_reload()
