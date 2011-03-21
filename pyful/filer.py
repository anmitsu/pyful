# filer.py - file management interface
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

import curses
import fnmatch
import glob
import grp
import os
import pwd
import re
import stat
import time

from pyful import look
from pyful import message
from pyful import ui
from pyful import util

class Filer(ui.Component):
    def __init__(self):
        ui.Component.__init__(self, "Filer")
        self.workspaces = []
        self.cursor = 0

    @property
    def keymap(self):
        return Directory.keymap

    @property
    def workspace(self):
        return self.workspaces[self.cursor]

    @property
    def dir(self):
        return self.workspace.dir

    @property
    def file(self):
        return self.workspace.dir.file

    @property
    def finder(self):
        return self.workspace.dir.finder

    def view(self):
        self.titlebar_view()
        self.workspace.view()

    def input(self, meta, key):
        self.dir.input(meta, key)

    def create_workspace(self, title=None):
        if title is None:
            title = str(len(self.workspaces)+1)
        self.workspaces.append(Workspace(title))
        self.workspaces[-1].create_dir(os.environ['HOME']).create_dir(os.environ['HOME'])
        self.focus_workspace(len(self.workspaces) - 1)
        self.workspace.resize()
        return self

    def close_workspace(self, x=None):
        if x is None:
            x = self.cursor
        if len(self.workspaces) <= 1:
            return

        self.workspaces[x].clear()
        ws = self.workspaces[x]
        self.workspaces.remove(ws)
        if not 0 <= self.cursor < len(self.workspaces):
            self.cursor = len(self.workspaces) - 1
        self.focus_workspace(self.cursor)
        return ws

    def focus_workspace(self, x):
        if not 0 <= x < len(self.workspaces):
            return
        self.workspace.clear()
        self.cursor = x
        self.workspace.resize()

    def mvdir_workspace_to(self, x):
        d = self.workspace.close_dir()
        if d is None:
            return
        self.workspaces[x].dirs.insert(0, d)
        self.workspaces[x].setcursor(0)
        self.workspace.resize()

    def mvfocus(self, x):
        self.workspace.clear()
        self.cursor += x
        if self.cursor >= len(self.workspaces):
            self.cursor = 0
        elif self.cursor < 0:
            self.cursor = len(self.workspaces) - 1
        self.workspace.resize()

    def next_workspace(self):
        self.mvfocus(+1)

    def prev_workspace(self):
        self.mvfocus(-1)

    def swap_workspace_inc(self):
        ws = self.workspace
        self.workspaces.remove(ws)
        if self.cursor < len(self.workspaces):
            self.workspaces.insert(self.cursor+1, ws)
            self.cursor += 1
        else:
            self.workspaces.insert(0, ws)
            self.cursor = 0

    def swap_workspace_dec(self):
        ws = self.workspace
        self.workspaces.remove(ws)
        if self.cursor > 0:
            self.workspaces.insert(self.cursor-1, ws)
            self.cursor -= 1
        else:
            self.workspaces.insert(len(self.workspaces), ws)
            self.cursor = len(self.workspaces) - 1

    def titlebar_view(self):
        titlebar = ui.getcomponent("Titlebar").win
        titlebar.erase()
        titlebar.move(0, 0)

        length = sum([util.termwidth(w.title)+2 for w in self.workspaces])

        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        if x-length < 5:
            return message.error('terminal size very small')

        for i, ws in enumerate(self.workspaces):
            if self.cursor == i:
                titlebar.addstr(' '+ws.title+' ', look.colors['WorkspaceFocus'])
            else:
                titlebar.addstr(' '+ws.title+' ')
        titlebar.addstr(' | ', curses.A_BOLD)

        dirlen = len(self.workspace.dirs)
        width = (x-length-4) // dirlen
        odd = (x-length-4) % dirlen
        if width < 5:
            titlebar.noutrefresh()
            return message.error('terminal size very small')

        for i, path in enumerate([d.path for d in self.workspace.dirs]):
            num = '[{0}] '.format(i+1)
            numlen = len(num)
            path = path.replace(os.environ['HOME'], "~", 1)
            if path.endswith(os.sep):
                path = util.path_omission(path, width-numlen-1)
            else:
                path = util.path_omission(path, width-numlen-1-len(os.sep)) + os.sep
            if i == 0:
                w = width-numlen+odd
            else:
                w = width-numlen
            string = num + util.mbs_rjust(path, w)
            if i == self.workspace.cursor:
                titlebar.addstr(string, look.colors['TitlebarFocus'])
            else:
                titlebar.addstr(string)
        titlebar.noutrefresh()

    def toggle_view_ext(self):
        FileStat.view_ext = not FileStat.view_ext
        self.workspace.all_reload()

    def toggle_view_permission(self):
        FileStat.view_permission = not FileStat.view_permission
        self.workspace.all_reload()

    def toggle_view_nlink(self):
        FileStat.view_nlink = not FileStat.view_nlink
        self.workspace.all_reload()

    def toggle_view_user(self):
        FileStat.view_user = not FileStat.view_user
        self.workspace.all_reload()

    def toggle_view_group(self):
        FileStat.view_group = not FileStat.view_group
        self.workspace.all_reload()

    def toggle_view_size(self):
        FileStat.view_size = not FileStat.view_size
        self.workspace.all_reload()

    def toggle_view_mtime(self):
        FileStat.view_mtime = not FileStat.view_mtime
        self.workspace.all_reload()

    def default_init(self):
        for i in range(0, 5):
            self.workspaces.append(Workspace(str(i+1)))
            self.workspaces[-1].dirs.append(Directory(os.environ['HOME'], 10, 10, 1, 0))
            self.workspaces[-1].dirs.append(Directory(os.environ['HOME'], 10, 10, 1, 0))

    def savefile(self, path):
        path = os.path.expanduser(path)
        try:
            f = open(path, 'w')
        except IOError:
            os.makedirs(util.unix_dirname(path))
            f = open(path, 'w')
        f.write('[workspace size]'+os.linesep)
        f.write(str(len(self.workspaces))+os.linesep)
        for ws in self.workspaces:
            f.write('[workspace title]'+os.linesep)
            f.write(ws.title+os.linesep)
            f.write('[workspace size]'+os.linesep)
            f.write(str(len(ws.dirs))+os.linesep)
            for d in ws.dirs:
                f.write('[workspace path]'+os.linesep)
                f.write(d.path+os.linesep)
                f.write('[sort kind]'+os.linesep)
                f.write(d.sort_kind+os.linesep)
        f.close()

    def loadfile(self, path):
        try:
            f = open(os.path.expanduser(path), 'r')
            f.readline()
            self.workspaces = []
            ws_i = int(f.readline().rstrip(os.linesep))
            for i in range(0, ws_i):
                f.readline()
                title = f.readline().rstrip(os.linesep)
                self.workspaces.append(Workspace(title))

                f.readline()
                d_i = int(f.readline().rstrip(os.linesep))
                for j in range(0, d_i):
                    f.readline()
                    path = f.readline().rstrip(os.linesep)
                    self.workspaces[-1].dirs.append(Directory(path, 10, 10, 1, 0))
                    f.readline()
                    self.workspaces[-1].dirs[-1].sort_kind = f.readline().rstrip(os.linesep)
            f.close()
        except:
            pass
        if len(self.workspaces) == 0:
            for i in range(0, 5):
                self.workspaces.append(Workspace(str(i+1)))
                self.workspaces[-1].dirs.append(Directory(os.environ['HOME'], 10, 10, 1, 0))
                self.workspaces[-1].dirs.append(Directory(os.environ['HOME'], 10, 10, 1, 0))
        self.workspace.resize()

class Workspace(object):
    default_path = '~/'
    layout = 'Tile'

    def __init__(self, title):
        self.title = title
        self.dirs = []
        self.cursor = 0

    @property
    def dir(self):
        return self.dirs[self.cursor]

    @property
    def nextdir(self):
        s = self.cursor + 1
        if s >= len(self.dirs):
            return self.dirs[0]
        else:
            return self.dirs[s]

    @property
    def prevdir(self):
        s= self.cursor - 1
        if s < 0:
            return self.dirs[-1]
        else:
            return self.dir[s]

    def create_dir(self, path=None):
        if path is None:
            path = self.default_path
        path = os.path.expanduser(path)
        size = len(self.dirs)
        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        height = y - 3
        width = x // (size+1)
        begy = 1
        begx = width * size

        self.dirs.insert(0, Directory(path, height, width, begy, begx))
        self.setcursor(0)
        self.dir.chdir(path)
        self.resize()
        return self

    def close_dir(self, x=None):
        if x is None:
            x = self.cursor
        if len(self.dirs) <= 1:
            return
        d = self.dirs[x]
        self.dirs.remove(d)
        if self.cursor > len(self.dirs) - 1:
            self.cursor = len(self.dirs)-1
        self.setcursor(self.cursor)
        self.resize()
        return d

    def chtitle(self, title):
        self.title = title

    def resize(self):
        if self.layout == 'Tile':
            self.tile()
        if self.layout == 'Tile reverse':
            self.tile(reverse=True)
        elif self.layout == 'Oneline':
            self.oneline()
        elif self.layout == 'Onecolumn':
            self.onecolumn()
        elif self.layout == 'Fullscreen':
            self.fullscreen()
        return self

    def tile(self, reverse=False):
        if reverse:
            self.layout = 'Tile reverse'
        else:
            self.layout = 'Tile'
        size = len(self.dirs)

        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        height = y - (ui.getcomponent("Cmdscr").win.getmaxyx()[0] + ui.getcomponent("Titlebar").win.getmaxyx()[0])
        if size == 1:
            self.dirs[0].resize(height, x, 1, 0)
        else:
            width = x // 2
            wodd = x % 2

            if reverse:
                self.dirs[0].resize(height, width, 1, width)
            else:
                self.dirs[0].resize(height, width, 1, 0)

            size -= 1
            odd = height % size
            height //= size
            for i in range(0, size):
                if i == size-1:
                    if reverse:
                        self.dirs[i+1].resize(height+odd, width+wodd, height*i+1, 0)
                    else:
                        self.dirs[i+1].resize(height+odd, width+wodd, height*i+1, width)
                else:
                    if reverse:
                        self.dirs[i+1].resize(height, width+wodd, height*i+1, 0)
                    else:
                        self.dirs[i+1].resize(height, width+wodd, height*i+1, width)
        self.all_reload()

    def oneline(self):
        self.layout = 'Oneline'
        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        height = y - (ui.getcomponent("Cmdscr").win.getmaxyx()[0] + ui.getcomponent("Titlebar").win.getmaxyx()[0])
        k = len(self.dirs)
        width = x // k
        odd = x % k
        for i, d in enumerate(self.dirs[:-1]):
            d.resize(height, width, 1, width*i)
        self.dirs[-1].resize(height, width+odd, 1, width*(k-1))
        self.all_reload()

    def onecolumn(self):
        self.layout = 'Onecolumn'
        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        y -= ui.getcomponent("Cmdscr").win.getmaxyx()[0] + ui.getcomponent("Titlebar").win.getmaxyx()[0]
        k = len(self.dirs)
        odd = y % k
        height = y // k
        width = x
        for i, d in enumerate(self.dirs[:-1]):
            d.resize(height, width, height*i+1, 0)
        self.dirs[-1].resize(height+odd, width, height*(k-1)+1, 0)
        self.all_reload()

    def fullscreen(self):
        self.layout = 'Fullscreen'
        (y, x) = ui.getcomponent("Stdscr").win.getmaxyx()
        height = y - (ui.getcomponent("Cmdscr").win.getmaxyx()[0] + ui.getcomponent("Titlebar").win.getmaxyx()[0])
        width = x
        for d in self.dirs:
            d.resize(height, width, 1, 0)
        self.all_reload()

    def mvcursor(self, x):
        self.cursor += x
        if len(self.dirs) <= self.cursor:
            self.cursor = 0
        elif self.cursor < 0:
            self.cursor = len(self.dirs) - 1
        try:
            os.chdir(self.dir.path)
        except Exception as e:
            message.exception(e)
            self.dir.chdir(self.default_path)
        return self.cursor

    def setcursor(self, x):
        if not 0 <= x < len(self.dirs):
            return
        self.cursor = x
        try:
            os.chdir(self.dir.path)
        except Exception as e:
            message.exception(e)
            self.dir.chdir(self.default_path)
        return self.cursor

    def swap_dir_inc(self):
        d = self.dir
        self.dirs.remove(d)
        if self.cursor < len(self.dirs):
            self.dirs.insert(self.cursor+1, d)
            self.cursor += 1
        else:
            self.dirs.insert(0, d)
            self.cursor = 0
        self.resize()
        return self

    def swap_dir_dec(self):
        d = self.dir
        self.dirs.remove(d)
        if self.cursor > 0:
            self.dirs.insert(self.cursor-1, d)
            self.cursor -= 1
        else:
            self.dirs.insert(len(self.dirs), d)
            self.cursor = len(self.dirs) - 1
        self.resize()
        return self

    def focus_reload(self):
        self.dir.reload()
        os.chdir(self.dir.path)

    def all_reload(self):
        for d in self.dirs:
            d.reload()
        os.chdir(self.dir.path)
        return self

    def clear(self):
        for d in self.dirs:
            d.files[:] = []

    def view(self):
        if self.layout == 'Fullscreen':
            self.dir.view(True)
        else:
            for i, d in enumerate(self.dirs):
                if i != self.cursor:
                    d.view(False)
            self.dir.view(True)

class Directory(object):
    sort_kind = 'Name[^]'
    scroll_type = 'HalfScroll'
    statusbar_format = " [{MARK}/{FILE}] {MARKSIZE}bytes {SCROLL}({CURSOR}) {SORT} "
    keymap = {}

    def __init__(self, path, height, width, begy, begx):
        self.win = curses.newwin(height, width, begy, begx)
        self.win.bkgd(look.colors['Window'])
        self.statwin = curses.newwin(1, self.win.getmaxyx()[0], self.win.getmaxyx()[1], self.win.getbegyx()[1])
        self.statwin.bkgd(look.colors['Window'])
        self.path = util.abspath(path)
        self.files = [FileStat(os.pardir)]
        self.mark_files = {}
        self.mark_size = '0'
        self.cursor = 0
        self.scrolltop = 0
        self.maskreg = None
        self.list = None
        self.list_title = None
        self.finder = Finder(self)
        self.history = PathHistory(self)

    @property
    def file(self):
        try:
            return self.files[self.cursor]
        except IndexError:
            return self.files[0]

    def input(self, meta, key):
        if self.finder.active:
            if not self.finder.input(meta, key):
                return
        keymap = self.keymap
        f = self.file
        ext  = util.extname(f.name)
        if ext != '' and (meta, key, ext) in keymap:
            keymap[(meta, key, ext)]()
        elif self.file.marked and (meta, key, '.mark') in keymap:
            keymap[(meta, key, '.mark')]()
        elif f.islink() and (meta, key, '.link') in keymap:
            keymap[(meta, key, '.link')]()
        elif f.isdir() and (meta, key, '.dir') in keymap:
            keymap[(meta, key, '.dir')]()
        elif f.isexec() and (meta, key, '.exec') in keymap:
            keymap[(meta, key, '.exec')]()
        else:
            if (meta, key) in keymap:
                keymap[(meta, key)]()

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.files) - 1

    def mvcursor(self, x):
        self.cursor += x

    def setcursor(self, x):
        self.cursor = x

    def pagedown(self):
        height = self.win.getmaxyx()[0] - self.statwin.getmaxyx()[0] - 1
        size = len(self.files)
        if self.scrolltop+height >= size:
            return
        [f.cache_clear() for f in self.files[self.scrolltop:self.scrolltop+height]]
        self.scrolltop += height
        self.cursor += height

    def pageup(self):
        if self.scrolltop == 0:
            return
        height = self.win.getmaxyx()[0] - self.statwin.getmaxyx()[0] - 1
        [f.cache_clear() for f in self.files[self.scrolltop:self.scrolltop+height]]
        self.scrolltop -= height
        self.cursor -= height

    def enter_dir(self):
        self.chdir(self.file.name)

    def enter_link(self):
        if self.file.isdir():
            self.enter_dir()

    def mask(self, regexp):
        self.maskreg = regexp
        self.reload()

    def glob(self, pattern):
        self.list_title = 'Grob:({0})'.format(pattern)
        self.list = list(glob.iglob(pattern))
        self.reload()

    def globdir(self, pattern):
        self.list_title = 'Grobdir:({0})'.format(pattern)

        def _globdir(dirname, patternname):
            try:
                li = os.listdir(dirname)
            except OSError:
                return
            for e in li:
                entrypath = os.path.join(dirname, e)
                if os.path.isdir(entrypath):
                    for ep in _globdir(entrypath, patternname):
                        yield ep
                if fnmatch.fnmatch(util.U(e), patternname):
                    yield os.path.normpath(entrypath)

        self.list = list(_globdir(os.curdir, pattern))
        self.reload()

    def open_listfile(self, path):
        self.list_title = "File:({0})".format(path)
        self.list = []
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip(os.linesep)
                    if os.path.exists(line):
                        self.list.append(re.sub(self.path+'?'+os.sep, '', line))
        except Exception as e:
            message.exception(e)
        self.reload()

    def reset(self):
        if self.ismark():
            self.mark_clear()
        elif self.list is not None:
            self.list = None
            self.list_title = None
            self.reload()
        elif self.maskreg is not None:
            self.maskreg = None
            self.reload()

    def diskread(self):
        marks = self.mark_files.copy()
        self.files[:] = [FileStat(os.pardir)]
        self.mark_files.clear()

        if self.finder.active:
            filelist = self.finder.results
        elif self.list is not None:
            filelist = self.list
        else:
            filelist = os.listdir(self.path)

        for f in filelist:
            if not os.path.lexists(f):
                continue
            if self.maskreg:
                if not os.path.isdir(f) and not self.maskreg.search(f):
                    continue
            try:
                fs = FileStat(f)
            except InvalidEncodingError:
                continue
            if fs.name in marks:
                fs.marked = True
                self.mark_files[fs.name] = fs
            self.files.append(fs)
        return self

    def reload(self):
        try:
            os.chdir(self.path)
            self.diskread()
            self.sort()
        except Exception as e:
            message.exception(e)
            self.chdir(Workspace.default_path)
        return self

    def chdir(self, path):
        self.list = None
        self.list_title = None
        if self.finder.active:
            self.finder.finish()

        self.mark_files.clear()
        self.mark_size = '0'

        parent_path = util.unix_dirname(self.path)
        parent_fname = util.unix_basename(self.path)
        path = util.abspath(util.expanduser(path), self.path)
        try:
            os.chdir(path)
        except Exception as e:
            return message.exception(e)

        self.history.update(path)
        self.path = path
        self.diskread()
        self.sort()

        if self.path == parent_path:
            self.setcursor(self.get_index(parent_fname))
        else:
            self.setcursor(0)
        return self

    def get_index(self, fname):
        for i, f in enumerate(self.files):
            if fname == f.name:
                return i
        return 0

    def markon(self):
        f = self.file
        if f.name == os.pardir:
            return
        f.marked = True
        self.mark_files[f.name] = f
        self.mark_size = self.get_mark_size()

    def markoff(self):
        f = self.file
        if f.name == os.pardir:
            return
        f.marked = False
        self.mark_files.pop(f.name)
        self.mark_size = self.get_mark_size()

    def mark_toggle(self):
        f = self.file
        if f.name == os.pardir:
            return self.mvcursor(+1)
        if f.marked:
            f.marked = False
            self.mark_files.pop(f.name)
        else:
            f.marked = True
            self.mark_files[f.name] = f
        self.mark_size = self.get_mark_size()
        self.mvcursor(+1)

    def mark_toggle_all(self):
        self.mark_files.clear()
        for f in self.files:
            if f.name == os.pardir:
                continue
            f.marked = not f.marked
            if f.marked:
                self.mark_files[f.name] = f
        self.mark_size = self.get_mark_size()

    def mark(self, pattern):
        for f in self.files:
            if f.name == os.pardir:
                continue
            if pattern.search(f.name):
                f.marked = True
                self.mark_files[f.name] = f
        self.mark_size = self.get_mark_size()

    def mark_below_cursor(self, filetype='all'):
        self.mark_all(filetype, self.cursor)

    def mark_all(self, filetype='all', start=0):
        self.mark_files.clear()
        for f in self.files[start:]:
            if f.name == os.pardir:
                continue
            if filetype == 'all':
                f.marked = True
                self.mark_files[f.name] = f
            elif filetype == 'file':
                if not f.isdir():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'directory':
                if f.isdir():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'symlink':
                if f.islink():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'executable':
                if f.isexec() and not f.isdir():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'socket':
                if f.issocket():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'fifo':
                if f.isfifo():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'chr':
                if f.ischr():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
            elif filetype == 'block':
                if f.isblock():
                    f.marked = True
                    self.mark_files[f.name] = f
                else:
                    f.marked = False
        self.mark_size = self.get_mark_size()

    def mark_clear(self):
        for f in self.files:
            f.marked = False
        self.mark_files.clear()
        self.mark_size = '0'

    def get_mark_size(self):
        if not self.mark_files:
            return '0'
        ret = 0
        for f in self.mark_files.values():
            if f.isdir():
                continue
            ret += f.stat.st_size
        return re.sub(r'(\d)(?=(?:\d\d\d)+(?!\d))', r'\1,', str(ret))

    def get_mark_files(self):
        if len(self.mark_files) == 0:
            return [self.file.name]
        else:
            return [f.name for f in self.mark_files.values()]

    def ismark(self):
        return len(self.mark_files) != 0

    def sort(self):
        if self.sort_kind == 'Name[^]': self.sort_name()
        elif self.sort_kind == 'Name[$]': self.sort_name_rev()
        elif self.sort_kind == 'Size[^]': self.sort_size()
        elif self.sort_kind == 'Size[$]': self.sort_size_rev()
        elif self.sort_kind == 'Time[^]': self.sort_time()
        elif self.sort_kind == 'Time[$]': self.sort_time_rev()
        elif self.sort_kind == 'Permission[^]': self.sort_permission()
        elif self.sort_kind == 'Permission[$]': self.sort_permission_rev()
        elif self.sort_kind == 'Link[^]': self.sort_nlink()
        elif self.sort_kind == 'Link[$]': self.sort_nlink_rev()
        elif self.sort_kind == 'Ext[^]': self.sort_ext()
        elif self.sort_kind == 'Ext[$]': self.sort_ext_rev()

    def sort_name(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            return util.cmp(x.name, y.name)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Name[^]'

    def sort_name_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            return util.cmp(y.name, x.name)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Name[$]'

    def sort_size(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(x.stat.st_size, y.stat.st_size)
            if ret == 0:
                return util.cmp(x.name, y.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Size[^]'

    def sort_size_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(y.stat.st_size, x.stat.st_size)
            if ret == 0:
                return util.cmp(y.name, x.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Size[$]'

    def sort_permission(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(x.stat.st_mode, y.stat.st_mode)
            if ret == 0:
                return util.cmp(x.name, y.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Permission[^]'

    def sort_permission_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(y.stat.st_mode, x.stat.st_mode)
            if ret == 0:
                return util.cmp(y.name, x.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Permission[$]'

    def sort_time(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(x.stat.st_mtime, y.stat.st_mtime)
            if ret == 0:
                return util.cmp(x.name, y.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Time[^]'

    def sort_time_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(y.stat.st_mtime, x.stat.st_mtime)
            if ret == 0:
                return util.cmp(y.name, x.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Time[$]'

    def sort_nlink(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(x.stat.st_nlink, y.stat.st_nlink)
            if ret == 0:
                return util.cmp(x.name, y.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Link[^]'

    def sort_nlink_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(y.stat.st_nlink, x.stat.st_nlink)
            if ret == 0:
                return util.cmp(y.name, x.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Link[$]'

    def sort_ext(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(util.extname(x.name), util.extname(y.name))
            if ret == 0:
                return util.cmp(x.name, y.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Ext[^]'

    def sort_ext_rev(self):
        def _sort(x, y):
            if x.name == os.pardir:
                return -1
            if y.name == os.pardir:
                return 1
            ret = util.cmp(util.extname(y.name), util.extname(x.name))
            if ret == 0:
                return util.cmp(y.name, x.name)
            else:
                return ret
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = 'Ext[$]'

    def resize(self, height, width, begy, begx):
        self.win.erase()
        self.statwin.erase()
        self.win = curses.newwin(height, width, begy, begx)
        begy, begx = self.win.getbegyx()
        self.statwin = curses.newwin(1, width, begy+height-1, begx)
        self.win.bkgd(look.colors['Window'])
        self.statwin.bkgd(look.colors['Window'])

    def scroll(self):
        height = self.win.getmaxyx()[0] - self.statwin.getmaxyx()[0] - 1
        [f.cache_clear() for f in self.files[self.scrolltop:self.scrolltop+height]]
        if self.scroll_type == 'HalfScroll':
            self.scrolltop = self.cursor - (height//2)
        elif self.scroll_type == 'PageScroll':
            self.scrolltop = (self.cursor//height) * height
        elif self.scroll_type == 'ContinuousScroll':
            if self.cursor >= self.scrolltop+height:
                self.scrolltop = self.cursor - height + 1
            elif self.cursor < self.scrolltop:
                self.scrolltop = self.cursor
        else:
            self.scrolltop = self.cursor - (height//2)

    def view(self, focus):
        size = len(self.files)
        height = self.win.getmaxyx()[0] - self.statwin.getmaxyx()[0] - 1
        width = self.win.getmaxyx()[1] - 3

        if not height: return

        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor >= size:
            self.cursor = size - 1

        if self.cursor >= self.scrolltop+height or self.cursor < self.scrolltop:
            self.scroll()

        if self.scrolltop < 0 or size < height:
            self.scrolltop = 0
        elif self.scrolltop >= size:
            self.scrolltop = (size//height) * height

        self.win.erase()
        ui.box(self.win)
        title = ""
        titlewidth = width
        if not self.path.endswith(os.sep):
            title += os.sep
            titlewidth -= len(os.sep)
        if self.maskreg:
            title += "{{{0}}}".format(self.maskreg.pattern)
            titlewidth -= util.termwidth(self.maskreg.pattern)
        title = util.path_omission(self.path.replace(os.environ['HOME'], '~', 1), titlewidth) + title
        self.win.move(0, 2)
        self.win.addstr(title, look.colors['DirectoryPath'])

        if width < 30:
            return message.error('terminal size very small')

        line = 0
        for i in range(self.scrolltop, size):
            line += 1
            if line > height:
                break

            f = self.files[i]
            fstr = f.get_view_file_string(self.path, width)

            if f.marked:
                if self.cursor == i and focus:
                    attr = look.colors['MarkFile'] | curses.A_REVERSE
                else:
                    attr = look.colors['MarkFile']
                self.win.move(line, 1)
                self.win.addstr('*' + fstr, attr)
            else:
                attr = f.get_attr()
                if self.cursor == i and focus:
                    attr += curses.A_REVERSE
                self.win.move(line, 1)
                self.win.addstr(' ' + fstr, attr)
        self.win.noutrefresh()

        self.statwin.erase()
        if not self.finder.active:
            ui.box(self.statwin)
        self.statwin.move(0, 1)

        if self.finder.active:
            if focus:
                self.file.view()
            self.finder.view()
        else:
            try:
                p = float(self.scrolltop)/float(size-height)*100
            except ZeroDivisionError:
                p = float(self.scrolltop)/float(size)*100
            if p == 0:
                p = 'Top'
            elif p >= 100:
                p = 'Bot'
            else:
                p = str(int(p)) + '%'

            status = self.statusbar_format.format(
                MARK=len(self.mark_files), FILE=size-1,
                MARKSIZE=self.mark_size, SCROLL=p,
                CURSOR=self.cursor, SORT=self.sort_kind)

            if self.list_title is not None:
                status += self.list_title

            (sy, sx) = self.statwin.getmaxyx()
            if util.termwidth(status) > sx-2:
                status = util.mbs_ljust(status, sx-2)
            self.statwin.addstr(status)
            self.statwin.noutrefresh()
            if focus:
                self.file.view()

class PathHistory(object):
    maxsave = 20

    def __init__(self, directory):
        self.dir = directory
        self.history = [self.dir.path]
        self.pos = 0
        self.updateflag = True

    def update(self, path):
        if not self.updateflag or path == self.history[self.pos]:
            return
        self.history = self.history[:self.pos+1]
        self.history.append(path)
        self.pos = len(self.history) - 1
        if self.maxsave < len(self.history):
            self.history = self.history[1:]
            self.pos = len(self.history) - 1

    def forward(self):
        self.mvhistory(1)

    def backward(self):
        self.mvhistory(-1)

    def mvhistory(self, x):
        self.mvpos(x)
        path = self.history[self.pos]
        if self.dir.path == path:
            return
        self.updateflag = False
        self.dir.chdir(path)
        self.updateflag = True

    def mvpos(self, x):
        self.pos += x
        if self.pos < 0:
            self.pos = 0
        elif self.pos >= len(self.history):
            self.pos = len(self.history) - 1

class Finder(object):
    keymap = {}
    smartcase = True
    migemo = None

    class History(object):
        history = [""]

        def __init__(self):
            self.pos = 0

        def add(self, string):
            if not string: return
            if string in self.history:
                self.history.remove(string)
            self.history.insert(1, string)

        def mvhistory(self, distance):
            self.pos += distance
            if self.pos < 0:
                self.pos = 0
            elif self.pos >= len(self.history) - 1:
                self.pos = len(self.history) - 1
            return self.history[self.pos]

    def __init__(self, dir):
        self.dir = dir
        self.results = []
        self.cache = []
        self.string = ""
        self.startfname = ""
        self.history = self.History()
        self.active = False
        self._stringcue = []

    def find(self, pattern):
        try:
            if self.smartcase and re.match("[A-Z]", pattern) is None:
                if self.migemo:
                    pattern = self.migemo.query(pattern)
                r = re.compile(pattern, re.IGNORECASE)
            else:
                if self.migemo:
                    pattern = self.migemo.query(pattern)
                r = re.compile(pattern)
        except (re.error, AssertionError):
            return
        self.results = [f for f in self.cache if r.search(f)]
        self.dir.reload()
        self.dir.setcursor(1)

    def insert(self, c):
        if len(self.results) <= 1:
            return
        try:
            s = util.U(c)
        except UnicodeError:
            self._stringcue.append(c)
            try:
                s = util.U("".join(self._stringcue))
                self._stringcue[:] = []
            except UnicodeError:
                return
        self.string += s
        self.find(self.string)

    def delete_backward_char(self):
        self.string = util.U(self.string)[:-1]
        self.find(self.string)

    def select_result(self):
        if len(self.dir.files) == 1:
            n = self.startfname
        else:
            n = self.dir.file.name
        self.dir.reload()
        self.dir.setcursor(self.dir.get_index(n))

    def history_select(self, distance):
        self.string = self.history.mvhistory(distance)
        self.find(self.string)

    def start(self):
        self.active = True
        self.results = self.cache = [f.name for f in self.dir.files if f.name != os.pardir]
        self.startfname = self.dir.file.name

    def finish(self):
        self.history.add(self.string)
        self.history.pos = 0
        self.string = ''
        self.results[:] = []
        self.cache[:] = []
        self.active = False
        self.select_result()

    def input(self, meta, key):
        try:
            c = chr(key)
        except ValueError:
            return
        if (meta, key) in self.keymap:
            self.keymap[(meta, key)]()
        elif c > " " and not meta:
            self.insert(c)
        else:
            return True
        
    def view(self):
        self.dir.statwin.move(0, 1)
        if self.migemo:
            self.dir.statwin.addstr(' Finder(migemo): ', look.colors['Finder'])
        else:
            self.dir.statwin.addstr(' Finder: ', look.colors['Finder'])
        try:
            self.dir.statwin.addstr(' ' + self.string)
        except Exception:
            message.error('Warning: status window very small')
        self.dir.statwin.noutrefresh()

class InvalidEncodingError(Exception):
    pass

class FileStat(object):
    view_ext = True
    view_permission = True
    view_nlink = False
    view_user = False
    view_group = False
    view_size = True
    view_mtime = True
    time_format = '%y-%m-%d %H:%M'
    time_24_flag = '!'
    time_week_flag = '#'
    time_yore_flag = ' '

    def __init__(self, name):
        self.marked = False
        self.view_file_string = None
        self.lstat = os.lstat(name)
        if self.islink():
            try:
                self.stat = os.stat(name)
            except OSError:
                self.stat = self.lstat
        else:
            self.stat = self.lstat
        try:
            self.name = util.U(name)
        except UnicodeError:
            self.name = name
            self.invalid_encoding_error()

    def isdir(self):
        return stat.S_ISDIR(self.stat.st_mode)

    def islink(self):
        return stat.S_ISLNK(self.lstat.st_mode)

    def isfifo(self):
        return stat.S_ISFIFO(self.stat.st_mode)

    def issocket(self):
        return stat.S_ISSOCK(self.stat.st_mode)

    def ischr(self):
        return stat.S_ISCHR(self.lstat.st_mode)

    def isblock(self):
        return stat.S_ISBLK(self.lstat.st_mode)

    def isexec(self):
        return stat.S_IEXEC & self.stat.st_mode

    def cache_clear(self):
        self.view_file_string = None

    def get_view_file_string(self, path, width):
        if self.view_file_string is None:
            fname = self.get_file_name(path)
            fstat = self.get_file_stat()
            fname = util.mbs_ljust(fname, width-util.termwidth(fstat))
            self.view_file_string = fname + fstat
        return self.view_file_string

    def get_file_name(self, path):
        if self.view_ext and not self.isdir() and not self.islink():
            fname = self.name.replace(util.extname(self.name), '')
        else:
            fname = self.name

        if self.islink():
            try:
                link = os.readlink(os.path.join(path, self.name))
            except:
                link = ''
            fname += '@ -> ' + link
            if self.isdir() and not link.endswith(os.sep):
                fname += os.sep
        elif self.isdir():
            fname += os.sep
        elif self.isfifo():
            fname += '|'
        elif self.issocket():
            fname += '='
        elif self.isexec():
            fname += '*'
        return fname

    def get_file_stat(self):
        fstat = ''
        if self.view_ext and not self.isdir() and not self.islink():
            fstat += ' {0}'.format(util.extname(self.name))
        if self.view_user:
            fstat += ' {0}'.format(self.get_user_name())
        if self.view_group:
            fstat += ' {0}'.format(self.get_group_name())
        if self.view_nlink:
            fstat += ' {0:>3}'.format(self.stat.st_nlink)
        if self.view_size:
            if self.isdir():
                fstat += ' {0:>7}'.format('<DIR>')
            else:
                fstat += ' {0:>7}'.format(self.get_file_size())
        if self.view_permission:
            fstat += ' {0}'.format(self.get_permission())
        if self.view_mtime:
            fstat += ' {0}'.format(self.get_mtime())
        return fstat

    def get_attr(self):
        if self.islink():
            if self.isdir():
                return look.colors['LinkDir']
            else:
                return look.colors['LinkFile']
        elif self.isdir():
            return look.colors['Directory']
        elif self.isexec():
            return look.colors['ExecutableFile']
        else:
            return 0

    def get_file_size(self):
        s = self.stat.st_size
        if s > 1024**3:
            return '{0:.1f}G'.format(float(s) / (1024**3))
        elif s > 1024**2:
            return '{0:.1f}M'.format(float(s) / (1024**2))
        elif s > 1024:
            return '{0:.1f}k'.format(float(s) / 1024)
        else:
            return str(s)

    def get_user_name(self):
        try:
            return pwd.getpwuid(self.stat.st_uid)[0]
        except KeyError:
            return 'unknown'

    def get_group_name(self):
        try:
            return grp.getgrgid(self.stat.st_gid)[0]
        except KeyError:
            return 'unknown'

    def get_mtime(self):
        tstr = time.strftime(self.time_format, time.localtime(self.stat.st_mtime))
        diff = time.time() - self.stat.st_mtime
        if diff < 60*60*24:
            return self.time_24_flag + tstr
        elif diff < 60*60*24*7:
            return self.time_week_flag + tstr
        else:
            return self.time_yore_flag + tstr

    def get_permission(self):
        perm = ''
        if stat.S_ISDIR(self.lstat.st_mode): perm += 'd'
        elif stat.S_ISLNK(self.lstat.st_mode): perm += 'l'
        elif stat.S_ISSOCK(self.lstat.st_mode): perm += 's'
        elif stat.S_ISFIFO(self.lstat.st_mode): perm += 'p'
        elif stat.S_ISCHR(self.lstat.st_mode): perm += 'c'
        elif stat.S_ISBLK(self.lstat.st_mode): perm += 'b'
        else: perm += '-'

        if self.lstat.st_mode & stat.S_IRUSR: perm += 'r'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IWUSR: perm += 'w'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IXUSR: perm += 'x'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IRGRP: perm += 'r'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IWGRP: perm += 'w'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IXGRP: perm += 'x'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IROTH: perm += 'r'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IWOTH: perm += 'w'
        else: perm += '-'
        if self.lstat.st_mode & stat.S_IXOTH: perm += 'x'
        else: perm += '-'

        return perm

    def invalid_encoding_error(self):
        perm = self.get_permission()
        nlink = self.stat.st_nlink
        user = self.get_user_name()
        group = self.get_group_name()
        size = '{0} ({1})'.format(self.get_file_size(), self.stat.st_size)
        time = self.get_mtime()
        ret = message.confirm(
            'Invalid encoding error. What do you do?',
            ['ignore', 'delete'],
            ["The file of invalid encoding status", '-'*100,
             "Permission: {0}".format(perm), "Link: {0}".format(nlink),
             "User: {0}".format(user), "Group: {0}".format(group),
             "Size: {0}".format(size), "Time: {0}".format(time)])
        if ret == 'delete':
            import shutil
            if self.isdir():
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            raise InvalidEncodingError
        else:
            self.name = ""

    def view(self):
        cmdscr = ui.getcomponent("Cmdscr").win
        cmdscr.erase()

        perm = self.get_permission()
        user = self.get_user_name()
        group = self.get_group_name()
        nlink = self.stat.st_nlink
        size = self.stat.st_size
        mtime = time.strftime(self.time_format, time.localtime(self.stat.st_mtime))
        name = self.name

        fstat = '{0} {1} {2} {3} {4} {5} {6}'.format(perm, nlink, user, group, size, mtime, name)
        fstat = util.mbs_ljust(fstat, ui.getcomponent("Stdscr").win.getmaxyx()[1]-1)
        cmdscr.move(1, 0)
        cmdscr.addstr(fstat)
        cmdscr.noutrefresh()
