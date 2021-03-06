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
import errno
import fnmatch
import glob
import grp
import json
import os
import pwd
import re
import stat
import time

from pyful import look
from pyful import message
from pyful import util

from pyful.widget.base import StandardScreen, Screen, Widget
from pyful.widget.textbox import TextBox
from pyful.widget.listbox import ListBox, Entry

class NavigationBar(Widget):
    def __init__(self):
        Widget.__init__(self, "NavigationBar")
        self.refresh()

    def refresh(self):
        y, x = self.stdscr.getmaxyx()
        self.panel.resize(2, x, y-2, 0)
        self.panel.attr = look.colors["Window"]

    def draw(self, drawfunc, *args, **kwd):
        self.panel.create_window()
        try:
            drawfunc(self.panel.win, *args, **kwd)
        except curses.error:
            self.panel.win.noutrefresh()

class Filer(Widget):
    keymap = {}

    def __init__(self):
        Widget.__init__(self, "Filer")
        y, x = self.stdscr.getmaxyx()
        self.titlebar = curses.newwin(1, x, 0, 0)
        self.titlebar.bkgd(look.colors["Titlebar"])
        self.navigationbar = NavigationBar()
        self.workspaces = []
        self.cursor = 0
        self.default_init()

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

    @property
    def pager(self):
        return self.workspace.dir.pager

    def refresh(self):
        y, x = self.stdscr.getmaxyx()
        self.titlebar = curses.newwin(1, x, 0, 0)
        self.titlebar.bkgd(look.colors["Titlebar"])
        self.workspace.refresh()

    def draw(self, navigation=True):
        try:
            self.draw_titlebar()
        except curses.error:
            self.titlebar.noutrefresh()
        try:
            self.workspace.draw()
        except curses.error:
            pass
        if navigation:
            self.navigationbar.draw(self.file.draw)

    def input(self, key):
        if self.pager.active:
            self.pager.input(key)
            return
        if self.finder.active:
            if not self.finder.input(key):
                return
        kmap = self.keymap
        f = self.file
        ext = util.extname(f.name)
        if f.marked and (key, ".mark") in kmap:
            kmap[(key, ".mark")]()
        elif f.islink() and (key, ".link") in kmap:
            kmap[(key, ".link")]()
        elif f.isdir() and (key, ".dir") in kmap:
            kmap[(key, ".dir")]()
        elif f.isexec() and (key, ".exec") in kmap:
            kmap[(key, ".exec")]()
        elif ext and (key, ext) in kmap:
            kmap[(key, ext)]()
        else:
            if key in kmap:
                kmap[key]()

    def create_workspace(self, title=None):
        if title is None:
            title = str(len(self.workspaces)+1)
        ws = Workspace(title)
        ws.create_dir(os.getenv("HOME"))
        ws.create_dir(os.getenv("HOME"))
        self.workspaces.append(ws)
        self.focus_workspace(len(self.workspaces) - 1)
        self.workspace.refresh()

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
        self.workspace.refresh()

    def mvdir_workspace_to(self, x):
        d = self.workspace.close_dir()
        if d is None:
            return
        self.workspaces[x].dirs.insert(0, d)
        self.workspaces[x].setcursor(0)
        self.workspace.refresh()

    def mvfocus(self, x):
        self.workspace.clear()
        self.cursor += x
        if self.cursor >= len(self.workspaces):
            self.cursor = 0
        elif self.cursor < 0:
            self.cursor = len(self.workspaces) - 1
        self.workspace.refresh()

    def next_workspace(self):
        self.mvfocus(+1)

    def prev_workspace(self):
        self.mvfocus(-1)

    def swap_workspace(self, amount):
        new = self.cursor + amount
        if amount > 0:
            if new >= len(self.workspaces):
                new = 0
        else:
            if new < 0:
                new = len(self.workspaces) - 1
        ws = self.workspace
        self.workspaces.remove(ws)
        self.workspaces.insert(new, ws)
        self.cursor = new

    def swap_workspace_inc(self):
        self.swap_workspace(1)

    def swap_workspace_dec(self):
        self.swap_workspace(-1)

    def draw_titlebar(self):
        self.titlebar.erase()
        self.titlebar.move(0, 0)
        length = sum([util.termwidth(w.title)+2 for w in self.workspaces])
        y, x = self.stdscr.getmaxyx()

        for i, ws in enumerate(self.workspaces):
            if self.cursor == i:
                self.titlebar.addstr(" {0} ".format(ws.title), look.colors["WorkspaceFocus"])
            else:
                self.titlebar.addstr(" {0} ".format(ws.title))
        self.titlebar.addstr(" | ", curses.A_BOLD)

        dirlen = len(self.workspace.dirs)
        width = (x-length-4) // dirlen
        odd = (x-length-4) % dirlen

        for i, path in enumerate([d.path for d in self.workspace.dirs]):
            num = "[{0}] ".format(i+1)
            numlen = len(num)
            path = util.replhome(path)
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
                self.titlebar.addstr(string, look.colors["TitlebarFocus"])
            else:
                self.titlebar.addstr(string)
        self.titlebar.noutrefresh()

    def toggle_draw_ext(self):
        FileStat.draw_ext = not FileStat.draw_ext
        self.workspace.all_reload()

    def toggle_draw_permission(self):
        FileStat.draw_permission = not FileStat.draw_permission
        self.workspace.all_reload()

    def toggle_draw_nlink(self):
        FileStat.draw_nlink = not FileStat.draw_nlink
        self.workspace.all_reload()

    def toggle_draw_user(self):
        FileStat.draw_user = not FileStat.draw_user
        self.workspace.all_reload()

    def toggle_draw_group(self):
        FileStat.draw_group = not FileStat.draw_group
        self.workspace.all_reload()

    def toggle_draw_size(self):
        FileStat.draw_size = not FileStat.draw_size
        self.workspace.all_reload()

    def toggle_draw_mtime(self):
        FileStat.draw_mtime = not FileStat.draw_mtime
        self.workspace.all_reload()

    def default_init(self):
        self.workspaces[:] = []
        self.cursor = 0
        for i in range(0, 5):
            ws = Workspace(str(i+1))
            ws.dirs.append(Directory(os.getenv("HOME"), 1, 1, 1, 0))
            ws.dirs.append(Directory(os.getenv("HOME"), 1, 1, 1, 0))
            self.workspaces.append(ws)

    def savefile(self, path):
        path = os.path.expanduser(path)
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        obj = {}
        obj["FocusWorkspace"] = self.cursor
        obj["WorkspacesData"] = [
            {"title": ws.title,
             "layout": ws.layout,
             "focus": ws.cursor,
             "dirs": [{"path": d.path,
                       "sort": d.sort_kind,
                       "cursor": d.cursor,
                       "scrolltop": d.scrolltop,
                       } for d in ws.dirs],
             } for ws in self.workspaces]
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)

    def loadfile(self, path):
        try:
            path = os.path.expanduser(path)
            with open(path, "r") as f:
                obj = json.load(f)
        except Exception as e:
            if e[0] != errno.ENOENT:
                message.exception(e)
                message.error("InformationLoadError: {0}".format(path))
            return
        self.workspaces[:] = []
        try:
            self.cursor = obj.get("FocusWorkspace", 0)
            data = obj.get("WorkspacesData", [])
            for i, wmap in enumerate(data):
                title = wmap.get("title", str(i+1))
                ws = Workspace(title)
                ws.layout = wmap.get("layout", "Tile")
                ws.cursor = wmap.get("focus", 0)
                if "dirs" not in wmap:
                    ws.create_dir(os.getenv("HOME"))
                    ws.create_dir(os.getenv("HOME"))
                    self.workspaces.append(ws)
                    continue
                for dmap in wmap["dirs"]:
                    path = dmap.get("path", os.getenv("HOME"))
                    d = Directory(path, 1, 1, 1, 0)
                    d.sort_kind = dmap.get("sort", "Name[^]")
                    d.cursor = dmap.get("cursor", 0)
                    d.scrolltop = dmap.get("scrolltop", 0)
                    ws.dirs.append(d)
                self.workspaces.append(ws)
        except Exception as e:
            message.exception(e)
            self.default_init()
        if not 0 <= self.cursor < len(self.workspaces):
            self.cursor = 0
        self.workspace.refresh()

class Workspace(StandardScreen):
    default_path = os.getenv("HOME")
    layout = "Tile"

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
        s = self.cursor - 1
        if s < 0:
            return self.dirs[-1]
        else:
            return self.dir[s]

    def mvfocus(self):
        try:
            os.chdir(self.dir.path)
        except Exception as e:
            message.exception(e)
            self.dir.chdir(self.default_path)
        if self.layout == "Magnifier":
            self.magnifier()

    def mvcursor(self, amount):
        self.cursor += amount
        if len(self.dirs) <= self.cursor:
            self.cursor = 0
        elif self.cursor < 0:
            self.cursor = len(self.dirs) - 1
        self.mvfocus()

    def setcursor(self, dist):
        if 0 <= dist < len(self.dirs):
            self.cursor = dist
            self.mvfocus()

    def create_dir(self, path=None):
        if path is None:
            path = self.default_path
        path = os.path.expanduser(path)
        size = len(self.dirs)
        y, x = self.stdscr.getmaxyx()
        height = y - 3
        width = x // (size+1)
        begy = 1
        begx = width * size

        self.dirs.insert(0, Directory(path, height, width, begy, begx))
        self.setcursor(0)
        self.dir.chdir(path)
        self.refresh()
        return self

    def close_dir(self, x=None):
        if x is None:
            x = self.cursor
        if len(self.dirs) <= 1:
            return
        d = self.dirs[x]
        self.dirs.remove(d)
        if self.cursor > len(self.dirs) - 1:
            self.setcursor(len(self.dirs)-1)
        self.setcursor(self.cursor)
        self.refresh()
        return d

    def chtitle(self, title):
        self.title = title

    def refresh(self):
        if self.layout == "Tile":
            self.tile()
        elif self.layout == "TileLeft":
            self.tileleft()
        elif self.layout == "TileTop":
            self.tiletop()
        elif self.layout == "TileBottom":
            self.tilebottom()
        elif self.layout == "Oneline":
            self.oneline()
        elif self.layout == "Onecolumn":
            self.onecolumn()
        elif self.layout == "Magnifier":
            self.magnifier()
        elif self.layout == "Fullscreen":
            self.fullscreen()

    def tile(self):
        self.layout = "Tile"
        size = len(self.dirs)
        y, x = self.stdscr.getmaxyx()
        y -= 3
        if size == 1:
            self.dirs[0].resize(y, x, 1, 0)
            self.all_reload()
            return
        height = y
        width = x // 2
        wodd = x % 2
        self.dirs[0].resize(height, width, 1, 0)
        k = size - 1
        height = y // k
        hodd = y % k
        for i, d in enumerate(self.dirs[1:-1]):
            d.resize(height, width+wodd, height*i+1, width)
        self.dirs[-1].resize(height+hodd, width+wodd, height*(k-1)+1, width)
        self.all_reload()

    def tileleft(self):
        self.layout = "TileLeft"
        size = len(self.dirs)
        y, x = self.stdscr.getmaxyx()
        y -= 3
        if size == 1:
            self.dirs[0].resize(y, x, 1, 0)
            self.all_reload()
            return
        height = y
        width = x // 2
        wodd = x % 2
        self.dirs[0].resize(height, width, 1, width)
        k = size - 1
        height = y // k
        hodd = y % k
        for i, d in enumerate(self.dirs[1:-1]):
            d.resize(height, width+wodd, height*i+1, 0)
        self.dirs[-1].resize(height+hodd, width+wodd, height*(k-1)+1, 0)
        self.all_reload()

    def tiletop(self):
        self.layout = "TileTop"
        size = len(self.dirs)
        y, x = self.stdscr.getmaxyx()
        y -= 3
        if size == 1:
            self.dirs[0].resize(y, x, 1, 0)
            self.all_reload()
            return
        width = x
        height = y // 2
        hodd = y % 2
        self.dirs[0].resize(height, width, height+hodd+1, 0)
        k = size-1
        width = x // k
        wodd = x % k
        for i, d in enumerate(self.dirs[1:-1]):
            d.resize(height+hodd, width, 1, width*i)
        self.dirs[-1].resize(height+hodd, width+wodd, 1, width*(k-1))
        self.all_reload()

    def tilebottom(self):
        self.layout = "TileBottom"
        size = len(self.dirs)
        y, x = self.stdscr.getmaxyx()
        y -= 3
        if size == 1:
            self.dirs[0].resize(y, x, 1, 0)
            self.all_reload()
            return
        width = x
        height = y // 2
        hodd = y % 2
        self.dirs[0].resize(height, width, 1, 0)
        k = size-1
        width = x // k
        wodd = x % k
        for i, d in enumerate(self.dirs[1:-1]):
            d.resize(height+hodd, width, height+1, width*i)
        self.dirs[-1].resize(height+hodd, width+wodd, height+1, width*(k-1))
        self.all_reload()

    def oneline(self):
        self.layout = "Oneline"
        y, x = self.stdscr.getmaxyx()
        height = y - 3
        k = len(self.dirs)
        width = x // k
        odd = x % k
        for i, d in enumerate(self.dirs[:-1]):
            d.resize(height, width, 1, width*i)
        self.dirs[-1].resize(height, width+odd, 1, width*(k-1))
        self.all_reload()

    def onecolumn(self):
        self.layout = "Onecolumn"
        y, x = self.stdscr.getmaxyx()
        y -= 3
        k = len(self.dirs)
        odd = y % k
        height = y // k
        width = x
        for i, d in enumerate(self.dirs[:-1]):
            d.resize(height, width, height*i+1, 0)
        self.dirs[-1].resize(height+odd, width, height*(k-1)+1, 0)
        self.all_reload()

    def magnifier(self):
        self.layout = "Magnifier"
        y, x = self.stdscr.getmaxyx()
        y -= 3
        if len(self.dirs) == 1:
            self.dirs[0].resize(y, x, 1, 0)
            self.all_reload()
            return
        k = len(self.dirs)-1
        odd = y % k
        height = y // k
        width = x
        ratio = 0.8
        focusdir = self.dirs.pop(self.cursor)
        focusdir.resize(int(y*ratio), int(x*ratio),
                        (y-(int(y*ratio)))//2, (x-(int(x*ratio)))//2)
        for i, d in enumerate(self.dirs[:-1]):
            d.resize(height, width, height*i+1, 0)
        self.dirs[-1].resize(height+odd, width, height*(k-1)+1, 0)
        self.dirs.insert(self.cursor, focusdir)
        self.all_reload()

    def fullscreen(self):
        self.layout = "Fullscreen"
        y, x = self.stdscr.getmaxyx()
        height = y - 3
        width = x
        for d in self.dirs:
            d.resize(height, width, 1, 0)
        self.all_reload()

    def swap_dir(self, amount):
        new = self.cursor + amount
        if amount > 0:
            if new >= len(self.dirs):
                new = 0
        else:
            if new < 0:
                new = len(self.dirs) - 1
        d = self.dir
        self.dirs.remove(d)
        self.dirs.insert(new, d)
        self.setcursor(new)
        self.refresh()

    def swap_dir_inc(self):
        self.swap_dir(1)

    def swap_dir_dec(self):
        self.swap_dir(-1)

    def focus_reload(self):
        self.dir.reload()
        os.chdir(self.dir.path)

    def all_reload(self):
        for d in self.dirs:
            d.reload()
        os.chdir(self.dir.path)

    def clear(self):
        for d in self.dirs:
            d.screen.unlink_window()
            d.finder.panel.unlink_window()
            d.files[:] = []

    def draw(self):
        if self.layout == "Fullscreen":
            self.dir.draw(True)
        else:
            for i, d in enumerate(self.dirs):
                if i != self.cursor:
                    d.draw(False)
            self.dir.draw(True)

class Directory(StandardScreen):
    sort_kind = "Name[^]"
    sort_updir = False
    scroll_type = "HalfScroll"
    statusbar_format = " [{MARK}/{FILE}] {MARKSIZE}bytes {SCROLL}({CURSOR}) {SORT} "

    def __init__(self, path, height, width, begy, begx):
        self.screen = Screen(height, width, begy, begx)
        self.screen.attr = look.colors["Window"]
        self.screen.create_window()
        self.path = util.abspath(path)
        self.files = [FileStat(os.pardir)]
        self.mark_files = set()
        self.mark_size = "0"
        self.cursor = 0
        self.scrolltop = 0
        self.maskreg = None
        self.list = None
        self.list_title = None
        self.finder = Finder(self)
        self.pager = Pager(self)
        self.history = PathHistory(self)

    @property
    def file(self):
        try:
            return self.files[self.cursor]
        except IndexError:
            return self.files[0]

    def settop(self):
        self.cursor = 0

    def setbottom(self):
        self.cursor = len(self.files) - 1

    def mvcursor(self, x):
        self.cursor += x

    def setcursor(self, x):
        self.cursor = x

    def mvscroll(self, amount):
        y, x = self.screen.win.getmaxyx()
        height = y - 2
        bottom = self.scrolltop+height
        if amount > 0:
            if bottom >= len(self.files):
                return
            for f in self.files[self.scrolltop:self.scrolltop+amount]:
                f.cache_clear()
            self.scrolltop += amount
            if self.cursor < self.scrolltop:
                self.cursor = self.scrolltop
        else:
            if self.scrolltop == 0:
                return
            for f in self.files[bottom+amount:bottom]:
                f.cache_clear()
            self.scrolltop += amount
            bottom += amount
            if self.cursor >= bottom:
                self.cursor = bottom - 1

    def pagedown(self):
        height = self.screen.win.getmaxyx()[0] - 2
        size = len(self.files)
        if self.scrolltop+height >= size:
            return
        for f in self.files[self.scrolltop:self.scrolltop+height]:
            f.cache_clear()
        self.scrolltop += height
        self.cursor += height

    def pageup(self):
        if self.scrolltop == 0:
            return
        height = self.screen.win.getmaxyx()[0] - 2
        for f in self.files[self.scrolltop:self.scrolltop+height]:
            f.cache_clear()
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
        self.list_title = "Grob:({0})".format(pattern)
        self.list = list(glob.iglob(pattern))
        self.reload()

    def globdir(self, pattern):
        def _globdir(dirname):
            try:
                files = os.listdir(util.U(dirname))
            except OSError:
                return
            for f in files:
                try:
                    path = os.path.join(dirname, f)
                except UnicodeError:
                    continue
                if os.path.isdir(path) and not os.path.islink(path):
                    for sub in _globdir(path):
                        yield sub
                if fnmatch.fnmatch(f, pattern):
                    yield os.path.normpath(path)
        self.list_title = "Grobdir:({0})".format(pattern)
        self.list = list(_globdir(os.curdir))
        self.reload()

    def open_listfile(self, path):
        self.list_title = "File:({0})".format(path)
        self.list = []
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip(os.linesep)
                    if os.path.exists(line):
                        line = re.sub("{0}?{1}".format(self.path, os.sep), "", line)
                        self.list.append(line)
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
        marks = set(f.name for f in self.mark_files)
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
            try:
                fs = FileStat(f)
            except InvalidEncodingError:
                continue
            if self.maskreg:
                if not (fs.isdir() or self.maskreg.search(fs.name)):
                    continue
            self.files.append(fs)
        self.mark_update([f for f in self.files if f.name in marks])

    def reload(self):
        try:
            os.chdir(self.path)
            self.diskread()
            self.sort()
        except Exception as e:
            message.exception(e)
            self.chdir(Workspace.default_path)

    def chdir(self, path):
        parpath = util.unix_dirname(self.path)
        parfile = util.unix_basename(self.path)
        newpath = util.abspath(util.expanduser(path), self.path)
        if newpath == self.path:
            return

        self.list = None
        self.list_title = None
        if self.finder.active:
            self.finder.finish()
        self.mark_clear()

        try:
            os.chdir(newpath)
        except Exception as e:
            return message.exception(e)
        self.history.update(newpath)
        self.path = newpath
        self.diskread()
        self.sort()
        if self.path == parpath:
            self.setcursor(self.get_index(parfile))
        else:
            self.setcursor(0)

    def get_index(self, fname):
        for i, f in enumerate(self.files):
            if fname == f.name:
                return i
        return 0

    def mark(self, pattern):
        self.mark_clear()
        self.mark_update([f for f in self.files if pattern.search(f.name)])

    def mark_toggle(self):
        self.mark_update([self.file], toggle=True)
        self.mvcursor(+1)

    def mark_toggle_all(self):
        self.mark_update(self.files, toggle=True)

    def mark_below_cursor(self, filetype="all"):
        self.mark_all(filetype, self.cursor)

    def mark_all(self, filetype="all", start=0):
        if filetype == "file":
            files = [f for f in self.files[start:] if not f.isdir()]
        elif filetype == "directory":
            files = [f for f in self.files[start:] if f.isdir()]
        elif filetype == "symlink":
            files = [f for f in self.files[start:] if f.islink()]
        elif filetype == "executable":
            files = [f for f in self.files[start:] if f.isexec() and not f.isdir() and not f.islink()]
        elif filetype == "socket":
            files = [f for f in self.files[start:] if f.issocket()]
        elif filetype == "fifo":
            files = [f for f in self.files[start:] if f.isfifo()]
        elif filetype == "chr":
            files = [f for f in self.files[start:] if f.ischr()]
        elif filetype == "block":
            files = [f for f in self.files[start:] if f.isblock()]
        else:
            files = [f for f in self.files[start:]]
        self.mark_clear()
        self.mark_update(files)

    def mark_update(self, fstats, toggle=False):
        for fs in fstats:
            if fs.name == os.pardir:
                continue
            if toggle:
                if fs.marktoggle():
                    self.mark_files.add(fs)
                else:
                    self.mark_files.discard(fs)
            else:
                fs.markon()
                self.mark_files.add(fs)
        self.mark_size = self.get_mark_size()

    def mark_clear(self):
        for f in self.mark_files:
            f.markoff()
        self.mark_files.clear()
        self.mark_size = "0"

    def get_mark_size(self):
        if not self.mark_files:
            return "0"
        size = sum(f.stat.st_size for f in self.mark_files if not f.isdir())
        return re.sub(r"(\d)(?=(?:\d\d\d)+(?!\d))", r"\1,", str(size))

    def get_mark_files(self):
        return [f.name for f in self.mark_files] or [self.file.name]

    def ismark(self):
        return len(self.mark_files) != 0

    def sort(self):
        if self.sort_kind == "Name[^]": self.sort_name(rev=False)
        elif self.sort_kind == "Name[$]": self.sort_name(rev=True)
        elif self.sort_kind == "Size[^]": self.sort_size(rev=False)
        elif self.sort_kind == "Size[$]": self.sort_size(rev=True)
        elif self.sort_kind == "Time[^]": self.sort_time(rev=False)
        elif self.sort_kind == "Time[$]": self.sort_time(rev=True)
        elif self.sort_kind == "Permission[^]": self.sort_permission(rev=False)
        elif self.sort_kind == "Permission[$]": self.sort_permission(rev=True)
        elif self.sort_kind == "Link[^]": self.sort_nlink(rev=False)
        elif self.sort_kind == "Link[$]": self.sort_nlink(rev=True)
        elif self.sort_kind == "Ext[^]": self.sort_ext(rev=False)
        elif self.sort_kind == "Ext[$]": self.sort_ext(rev=True)

    def _sort_default(self, sortfunc, x, y, rev):
        if x.name == os.pardir:
            return -1
        if y.name == os.pardir:
            return 1
        if self.sort_updir:
            xdir = x.isdir()
            ydir = y.isdir()
            if xdir == ydir:
                return sortfunc(x, y, rev)
            else:
                return 1 if ydir == 1 else -1
        else:
            return sortfunc(x, y, rev)

    def sort_name(self, rev=False):
        def _namecompare(x, y, rev):
            if rev:
                return util.cmp(y.name, x.name)
            else:
                return util.cmp(x.name, y.name)
        _sort = lambda x, y: self._sort_default(_namecompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Name[$]" if rev else "Name[^]"

    def sort_size(self, rev=False):
        def _sizecompare(x, y, rev):
            if rev:
                ret = util.cmp(y.stat.st_size, x.stat.st_size) 
            else:
                ret = util.cmp(x.stat.st_size, y.stat.st_size)
            if ret == 0:
                return util.cmp(y.name, x.name) if rev else util.cmp(x.name, y.name)
            else:
                return ret
        _sort = lambda x, y: self._sort_default(_sizecompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Size[$]" if rev else "Size[^]"

    def sort_permission(self, rev=False):
        def _permcompare(x, y, rev):
            if rev:
                ret = util.cmp(y.stat.st_mode, x.stat.st_mode) 
            else:
                ret = util.cmp(x.stat.st_mode, y.stat.st_mode)
            if ret == 0:
                return util.cmp(y.name, x.name) if rev else util.cmp(x.name, y.name)
            else:
                return ret
        _sort = lambda x, y: self._sort_default(_permcompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Permission[$]" if rev else "Permission[^]"

    def sort_time(self, rev=False):
        def _timecompare(x, y, rev):
            if rev:
                ret = util.cmp(y.stat.st_mtime, x.stat.st_mtime) 
            else:
                ret = util.cmp(x.stat.st_mtime, y.stat.st_mtime)
            if ret == 0:
                return util.cmp(y.name, x.name) if rev else util.cmp(x.name, y.name)
            else:
                return ret
        _sort = lambda x, y: self._sort_default(_timecompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Time[$]" if rev else "Time[^]"

    def sort_nlink(self, rev=False):
        def _nlinkcompare(x, y, rev):
            if rev:
                ret = util.cmp(y.stat.st_nlink, x.stat.st_nlink) 
            else:
                ret = util.cmp(x.stat.st_nlink, y.stat.st_nlink)
            if ret == 0:
                return util.cmp(y.name, x.name) if rev else util.cmp(x.name, y.name)
            else:
                return ret
        _sort = lambda x, y: self._sort_default(_nlinkcompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Link[$]" if rev else "Link[^]"

    def sort_ext(self, rev=False):
        def _extcompare(x, y, rev):
            if rev:
                ret = util.cmp(util.extname(y.name), util.extname(x.name)) 
            else:
                ret = util.cmp(util.extname(x.name), util.extname(y.name)) 
            if ret == 0:
                return util.cmp(y.name, x.name) if rev else util.cmp(x.name, y.name)
            else:
                return ret
        _sort = lambda x, y: self._sort_default(_extcompare, x, y, rev)
        self.files.sort(key=util.cmp_to_key(_sort))
        self.sort_kind = "Ext[$]" if rev else "Ext[^]"

    def resize(self, height, width, begy, begx):
        self.screen.resize(height, width, begy, begx)
        self.screen.attr = look.colors["Window"]
        self.screen.create_window()
        self.finder.refresh()
        self.pager.refresh()

    def _fix_position(self, size, height):
        if self.cursor < 0:
            self.cursor = 0
        elif self.cursor >= size:
            self.cursor = size - 1

        if self.cursor >= self.scrolltop+height or self.cursor < self.scrolltop:
            for f in self.files[self.scrolltop:self.scrolltop+height]:
                f.cache_clear()
            if self.scroll_type == "HalfScroll":
                self.scrolltop = self.cursor - (height//2)
            elif self.scroll_type == "PageScroll":
                self.scrolltop = (self.cursor//height) * height
            elif self.scroll_type == "ContinuousScroll":
                if self.cursor >= self.scrolltop+height:
                    self.scrolltop = self.cursor - height + 1
                elif self.cursor < self.scrolltop:
                    self.scrolltop = self.cursor
            else:
                self.scrolltop = self.cursor - (height//2)

        if self.scrolltop < 0 or size < height:
            self.scrolltop = 0
        elif self.scrolltop >= size:
            self.scrolltop = (size//height) * height

    def _draw_titlebar(self, width):
        title = ""
        titlewidth = width
        if not self.path.endswith(os.sep):
            title += os.sep
            titlewidth -= len(os.sep)
        if self.maskreg:
            title += "{{{0}}}".format(self.maskreg.pattern)
            titlewidth -= util.termwidth(self.maskreg.pattern)
        path = util.replhome(self.path)
        path = util.path_omission(path, titlewidth)
        self.screen.win.addstr(0, 2, path+title, look.colors["DirectoryPath"])

    def _draw_statusbar(self, size, height):
        try:
            p = float(self.scrolltop)/float(size-height)*100
        except ZeroDivisionError:
            p = float(self.scrolltop)/float(size)*100
        if p == 0:
            p = "Top"
        elif p >= 100:
            p = "Bot"
        else:
            p = str(int(p)) + "%"
        status = self.statusbar_format.format(
            MARK=len(self.mark_files), FILE=size-1,
            MARKSIZE=self.mark_size, SCROLL=p,
            CURSOR=self.cursor, SORT=self.sort_kind)
        if self.list_title is not None:
            status += self.list_title

        y, x = self.screen.win.getmaxyx()
        if util.termwidth(status) > x-2:
            status = util.mbs_ljust(status, x-2)
        self.screen.win.addstr(y-1, 1, status)

    def draw(self, focus):
        if self.pager.active:
            self.pager.draw()
            return

        size = len(self.files)
        win = self.screen.win
        height = win.getmaxyx()[0] - 2
        width = win.getmaxyx()[1] - 3
        if self.finder.active:
            height -= self.finder.panel.y
        if not height:
            return

        win.erase()
        win.border(*self.borders)
        self._draw_titlebar(width)
        self._fix_position(size, height)

        line = 0
        for i in range(self.scrolltop, size):
            line += 1
            if line > height:
                break

            f = self.files[i]
            fstr = f.get_drawn_text(self.path, width)
            attr = f.get_attr()
            if self.cursor == i and focus:
                attr += curses.A_REVERSE
            if f.marked:
                win.addstr(line, 1, "*"+fstr, attr)
            else:
                win.addstr(line, 1, " "+fstr, attr)
        self._draw_statusbar(size, height)
        win.noutrefresh()

        if self.finder.active:
            self.finder.draw()

class PathHistory(object):
    maxsave = 20

    class Data(object):
        def __init__(self, path):
            self.path = path
            self.cursor = 0
            self.scrolltop = 0

    def __init__(self, directory):
        self.dir = directory
        self.history = [self.Data(self.dir.path)]
        self.pos = 0
        self.updateflag = True

    def update(self, path):
        if not self.updateflag or path == self.history[self.pos].path:
            return
        self._cursorupdate()
        self.history = self.history[:self.pos+1]
        self.history.append(self.Data(path))
        self.pos = len(self.history) - 1
        if self.maxsave < len(self.history):
            self.history = self.history[1:]
            self.pos = len(self.history) - 1

    def _cursorupdate(self):
        self.history[self.pos].cursor = self.dir.cursor
        self.history[self.pos].scrolltop = self.dir.scrolltop

    def forward(self):
        self.mvhistory(1)

    def backward(self):
        self.mvhistory(-1)

    def mvhistory(self, x):
        self._cursorupdate()
        self.mvpos(x)
        path = self.history[self.pos].path
        cursor = self.history[self.pos].cursor
        scrolltop = self.history[self.pos].scrolltop
        if self.dir.path == path:
            return
        self.updateflag = False
        self.dir.chdir(path)
        self.dir.setcursor(cursor)
        self.dir.scrolltop = scrolltop
        self.updateflag = True

    def mvpos(self, x):
        self.pos += x
        if self.pos < 0:
            self.pos = 0
        elif self.pos >= len(self.history):
            self.pos = len(self.history) - 1

class Pager(ListBox):
    def __init__(self, directory):
        ListBox.__init__(self)
        self.dir = directory

    def refresh(self):
        y, x = self.dir.screen.win.getmaxyx()
        by, bx = self.dir.screen.win.getbegyx()
        self.panel.resize(y, x, by, bx)

    def preview(self, path):
        path = os.path.expanduser(path)
        entries = []
        with open(path, "r") as fd:
            for line in fd:
                line = line.strip(os.linesep)
                try:
                    line = line.decode()
                    line = re.sub(r"[\r]", "", line).expandtabs()
                    attr = 0
                except UnicodeError:
                    line = "????? - Invalid encoding"
                    attr = look.colors["ErrorMessage"]
                entries.append(Entry(line, attr=attr))
        self.show(entries)

class Finder(TextBox):
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

    def __init__(self, directory):
        TextBox.__init__(self)
        self.dir = directory
        self.results = []
        self.cache = []
        self.startfname = ""
        self.history = self.History()
        self.refresh()

    def refresh(self):
        y, x = self.dir.screen.win.getmaxyx()
        by, bx = self.dir.screen.win.getbegyx()
        self.panel.resize(1, x-2, by+y-2, bx+1)
        self.panel.attr = look.colors["FinderWindow"]
        self.promptattr = look.colors["FinderPrompt"]

    def edithook(self):
        self.find(self.text)

    def find(self, pattern):
        if not pattern:
            self.results = self.cache
            self.dir.reload()
            return
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
        idx = self.dir.get_index(self.startfname)
        if idx:
            self.dir.setcursor(idx)
        else:
            self.dir.setcursor(1)

    def select_result(self):
        if len(self.dir.files) == 1:
            n = self.startfname
        else:
            n = self.dir.file.name
        self.dir.reload()
        self.dir.setcursor(self.dir.get_index(n))

    def history_select(self, distance):
        self.settext(self.history.mvhistory(distance))
        self.find(self.text)

    def start(self):
        if self.migemo:
            self.prompt = " Finder(migemo): "
        else:
            self.prompt = " Finder: "
        self.show()
        self.cache = [f.name for f in self.dir.files if f.name != os.pardir]
        self.startfname = self.dir.file.name
        self.find(self.text)

    def finish(self):
        self.history.add(self.text)
        self.history.pos = 0
        self.results[:] = []
        self.cache[:] = []
        self.hide()
        self.select_result()

    def input(self, key):
        if key in self.keymap:
            self.keymap[key]()
        elif util.mbslen(key) == 1:
            self.insert(key)
        else:
            return True

class InvalidEncodingError(Exception):
    pass

class FileStat(object):
    draw_ext = True
    draw_permission = True
    draw_nlink = False
    draw_user = False
    draw_group = False
    draw_size = True
    draw_mtime = True
    time_format = "%y-%m-%d %H:%M"
    time_24_flag = "!"
    time_week_flag = "#"
    time_yore_flag = " "

    def __init__(self, name):
        self.marked = False
        self.drawn_text = None
        self.lstat = self.stat = os.lstat(name)
        if self.islink():
            try:
                self.stat = os.stat(name)
            except OSError:
                pass
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

    def markon(self):
        self.marked = True

    def markoff(self):
        self.marked = False

    def marktoggle(self):
        self.marked = not self.marked
        return self.marked

    def cache_clear(self):
        self.drawn_text = None

    def get_drawn_text(self, path, width):
        if self.drawn_text is None:
            fname = self.get_file_name(path)
            fstat = self.get_file_stat()
            namewidth = width - util.termwidth(fstat)
            if namewidth <= 0:
                namewidth = 0
                fstat = util.mbs_ljust(fstat, width)
            fname = util.mbs_ljust(fname, namewidth)
            self.drawn_text = fname + fstat
        return self.drawn_text

    def get_file_name(self, path):
        if self.draw_ext and not self.isdir() and not self.islink():
            fname = os.path.splitext(self.name)[0]
        else:
            fname = self.name

        if self.islink():
            try:
                link = os.readlink(os.path.join(path, self.name))
            except OSError:
                link = ""
            fname += "@ -> " + link
            if self.isdir():
                fname += os.sep
        elif self.isdir():
            fname += os.sep
        elif self.isfifo():
            fname += "|"
        elif self.issocket():
            fname += "="
        elif self.isexec():
            fname += "*"
        return fname

    def get_file_stat(self):
        fstat = ""
        if self.draw_ext and not self.isdir() and not self.islink():
            fstat += " {0}".format(util.extname(self.name))
        if self.draw_user:
            fstat += " {0}".format(self.get_user_name())
        if self.draw_group:
            fstat += " {0}".format(self.get_group_name())
        if self.draw_nlink:
            fstat += " {0:>3}".format(self.stat.st_nlink)
        if self.draw_size:
            if self.isdir():
                fstat += " {0:>7}".format("<DIR>")
            else:
                fstat += " {0:>7}".format(self.get_file_size())
        if self.draw_permission:
            fstat += " {0}".format(self.get_permission())
        if self.draw_mtime:
            fstat += " {0}".format(self.get_mtime())
        return fstat

    def get_attr(self):
        if self.marked:
            return look.colors["MarkFile"]
        elif self.islink():
            if self.isdir():
                return look.colors["LinkDir"]
            else:
                return look.colors["LinkFile"]
        elif self.isdir():
            return look.colors["Directory"]
        elif self.isexec():
            return look.colors["ExecutableFile"]
        else:
            return 0

    def get_file_size(self):
        s = self.stat.st_size
        if s > 1024**3:
            return "{0:.1f}G".format(float(s) / (1024**3))
        elif s > 1024**2:
            return "{0:.1f}M".format(float(s) / (1024**2))
        elif s > 1024:
            return "{0:.1f}k".format(float(s) / 1024)
        else:
            return str(s)

    def get_user_name(self):
        try:
            return pwd.getpwuid(self.stat.st_uid)[0]
        except KeyError:
            return "unknown"

    def get_group_name(self):
        try:
            return grp.getgrgid(self.stat.st_gid)[0]
        except KeyError:
            return "unknown"

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
        perm = ["-"] * 10
        if stat.S_ISDIR(self.lstat.st_mode): perm[0] = "d"
        elif stat.S_ISLNK(self.lstat.st_mode): perm[0] = "l"
        elif stat.S_ISSOCK(self.lstat.st_mode): perm[0] = "s"
        elif stat.S_ISFIFO(self.lstat.st_mode): perm[0] = "p"
        elif stat.S_ISCHR(self.lstat.st_mode): perm[0] = "c"
        elif stat.S_ISBLK(self.lstat.st_mode): perm[0] = "b"
        if self.stat.st_mode & stat.S_IRUSR: perm[1] = "r"
        if self.stat.st_mode & stat.S_IWUSR: perm[2] = "w"
        if self.stat.st_mode & stat.S_IXUSR: perm[3] = "x"
        if self.stat.st_mode & stat.S_IRGRP: perm[4] = "r"
        if self.stat.st_mode & stat.S_IWGRP: perm[5] = "w"
        if self.stat.st_mode & stat.S_IXGRP: perm[6] = "x"
        if self.stat.st_mode & stat.S_IROTH: perm[7] = "r"
        if self.stat.st_mode & stat.S_IWOTH: perm[8] = "w"
        if self.stat.st_mode & stat.S_IXOTH: perm[9] = "x"
        return "".join(perm)

    def invalid_encoding_error(self):
        perm = self.get_permission()
        nlink = self.stat.st_nlink
        user = self.get_user_name()
        group = self.get_group_name()
        size = "{0} ({1})".format(self.get_file_size(), self.stat.st_size)
        mtime = self.get_mtime()
        ret = message.confirm(
            "Invalid encoding error. What do you do?",
            ["ignore", "delete"],
            ["The file of invalid encoding status", "-"*100,
             "Permission: {0}".format(perm), "Link: {0}".format(nlink),
             "User: {0}".format(user), "Group: {0}".format(group),
             "Size: {0}".format(size), "Time: {0}".format(mtime)])
        if ret == "delete":
            import shutil
            if self.isdir():
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            raise InvalidEncodingError
        else:
            self.name = ""

    def draw(self, win):
        win.erase()
        perm = self.get_permission()
        user = self.get_user_name()
        group = self.get_group_name()
        nlink = self.stat.st_nlink
        size = self.stat.st_size
        mtime = self.get_mtime()
        name = self.name
        fstat = "{0} {1} {2} {3} {4} {5} {6}".format(perm, nlink, user, group, size, mtime, name)
        win.addstr(1, 0, fstat)
        win.noutrefresh()
