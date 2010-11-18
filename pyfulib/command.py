# command.py - pyful command management
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
import sys
import re
import glob

from pyfulib.core import Pyful
from pyfulib import mode
from pyfulib import util
from pyfulib import filectrl
from pyfulib import process

pyful = Pyful()

_image_filter = re.compile('\.(jpe?g|gif|png|bmp|tiff|jp2|j2c|svg|eps)$')
_music_filter = re.compile('\.(ogg|mp3|flac|ape|tta|tak|mid|wma|wav)$')
_video_filter = re.compile('\.(avi|mkv|mp4|mpe?g|wmv|asf|rm|ram|ra)$')
_archive_filter = re.compile('\.(zip|rar|lzh|cab|tar|7z|gz|bz2|xz|taz|tgz|tbz|txz|yz2)$')
_source_filter = re.compile('\.(py|rb|hs|el|js|lua|java|c|cc|cpp|cs|pl|php)$')

commands = {
    'copy'     : lambda: _copy(),
    'delete'   : lambda: _delete(),
    'move'     : lambda: _move(),
    'link'     : lambda: _link(),
    'rename'   : lambda: _rename(),
    'symlink'  : lambda: _symlink(),
    'trashbox' : lambda: _trashbox(),
    'tar'      : lambda: _tar(),
    'tareach'  : lambda: _tareach(),
    'untar'    : lambda: _untar(),
    'zip'      : lambda: _zip(),
    'zipeach'  : lambda: _zipeach(),
    'unzip'    : lambda: _unzip(),
    'chdir'    : lambda: pyful.cmdline.start(mode.Chdir(), pyful.filer.dir.path),
    'chmod'    : lambda: pyful.cmdline.start(mode.Chmod(), ''),
    'chown'    : lambda: pyful.cmdline.start(mode.Chown(), ''),
    'glob'     : lambda: pyful.cmdline.start(mode.Glob(), ''),
    'globdir'  : lambda: pyful.cmdline.start(mode.GlobDir(), ''),
    'mark'     : lambda: pyful.cmdline.start(mode.Mark(), ''),
    'mask'     : lambda: pyful.cmdline.start(mode.Mask(), ''),
    'menu'     : lambda: pyful.cmdline.start(mode.Menu(), ''),
    'mkdir'    : lambda: pyful.cmdline.start(mode.Mkdir(), ''),
    'replace'  : lambda: pyful.cmdline.start(mode.Replace(), ''),
    'newfile'  : lambda: pyful.cmdline.start(mode.Newfile(), ''),
    'utime'    : lambda: pyful.cmdline.start(mode.Utime(), pyful.filer.file.name),
    'shell'    : lambda: pyful.cmdline.start(mode.Shell(), ''),
    'eval'     : lambda: pyful.cmdline.start(mode.Eval(), ''),
    'mx'       : lambda: pyful.cmdline.start(mode.Mx(), ''),

    'open_at_system' : lambda: process.spawn("xdg-open %f %&"),
    'open_listfile'  : lambda: pyful.cmdline.start(mode.OpenListfile(), ''),
    'zoom_infobox'   : lambda: pyful.cmdline.start(mode.ZoomInfoBox(), ''),
    'google_search'  : lambda: pyful.cmdline.start(mode.WebSearch('Google'), ''),
    'kill_thread'    : lambda: filectrl.kill_thread(),
    'drivejump'      : lambda: _drivejump(),
    'fileviewer'     : lambda: _fileviewer(),
    'pack'           : lambda: _pack(),
    'unpack'         : lambda: _unpack(),
    'unpack2'        : lambda: _unpack2(),
    'spawn_editor'   : lambda: _spawn_editor(),
    'spawn_shell'    : lambda: _spawn_shell(),
    'exit'           : lambda: _exit(),

    'reload_rcfile'  : lambda: pyful.load_rcfile(),
    'refresh_window' : lambda: pyful.refresh(),
    'rehash_programs': lambda: pyful.cmdline.completion.loadprograms(),

    'enter_mark': lambda: pyful.cmdline.start(mode.Shell(), ' %m', 1),
    'enter_exec': lambda: pyful.cmdline.start(mode.Shell(), ' ./%f', 1),
    'enter_dir' : lambda: pyful.filer.dir.enter_dir(),
    'enter_link': lambda: pyful.filer.dir.enter_link(),
    'enter_listfile': lambda: pyful.filer.dir.open_listfile(pyful.filer.file.name),

    'chdir_parent'   : lambda: pyful.filer.dir.chdir(os.pardir),
    'chdir_root'     : lambda: pyful.filer.dir.chdir('/'),
    'chdir_home'     : lambda: pyful.filer.dir.chdir(os.environ['HOME']),
    'chdir_neighbor' : lambda: pyful.filer.dir.chdir(pyful.filer.workspace.nextdir.path),
    'chdir_backward' : lambda: pyful.filer.dir.pathhistory_backward(),
    'chdir_forward'  : lambda: pyful.filer.dir.pathhistory_forward(),
    'finder_start'   : lambda: pyful.filer.finder.start(),

    'layout_tile'      : lambda: pyful.filer.workspace.tile(),
    'layout_tile_rev'  : lambda: pyful.filer.workspace.tile(reverse=True),
    'layout_oneline'   : lambda: pyful.filer.workspace.oneline(),
    'layout_onecolumn' : lambda: pyful.filer.workspace.onecolumn(),
    'layout_fullscreen': lambda: pyful.filer.workspace.fullscreen(),

    'switch_workspace'        : lambda: _switch_workspace(),
    'create_workspace'        : lambda: pyful.cmdline.start(mode.CreateWorkspace(), ''),
    'close_workspace'         : lambda: pyful.filer.close_workspace(),
    'change_workspace_title'  : lambda: pyful.cmdline.start(mode.ChangeWorkspaceTitle(), ""),
    'change_workspace_layout' : lambda: _change_workspace_layout(),
    'view_next_workspace'     : lambda: pyful.filer.next_workspace(),
    'view_prev_workspace'     : lambda: pyful.filer.prev_workspace(),
    'swap_workspace_inc'      : lambda: pyful.filer.swap_workspace_inc(),
    'swap_workspace_dec'      : lambda: pyful.filer.swap_workspace_dec(),

    'create_dir'      : lambda: pyful.filer.workspace.create_dir(),
    'close_dir'       : lambda: pyful.filer.workspace.close_dir(),
    'all_reload'      : lambda: pyful.filer.workspace.all_reload(),
    'swap_dir_inc'    : lambda: pyful.filer.workspace.swap_dir_inc(),
    'swap_dir_dec'    : lambda: pyful.filer.workspace.swap_dir_dec(),
    'focus_next_dir'  : lambda: pyful.filer.workspace.mvcursor(+1),
    'focus_prev_dir'  : lambda: pyful.filer.workspace.mvcursor(-1),

    'filer_cursor_down' : lambda: pyful.filer.dir.mvcursor(+1),
    'filer_cursor_up'   : lambda: pyful.filer.dir.mvcursor(-1),
    'filer_pagedown'    : lambda: pyful.filer.dir.pagedown(),
    'filer_pageup'      : lambda: pyful.filer.dir.pageup(),
    'filer_settop'      : lambda: pyful.filer.dir.settop(),
    'filer_setbottom'   : lambda: pyful.filer.dir.setbottom(),
    'filer_reset'       : lambda: pyful.filer.dir.reset(),

    'toggle_view_ext'        : lambda: pyful.filer.toggle_view_ext(),
    'toggle_view_permission' : lambda: pyful.filer.toggle_view_permission(),
    'toggle_view_nlink'      : lambda: pyful.filer.toggle_view_nlink(),
    'toggle_view_user'       : lambda: pyful.filer.toggle_view_user(),
    'toggle_view_group'      : lambda: pyful.filer.toggle_view_group(),
    'toggle_view_size'       : lambda: pyful.filer.toggle_view_size(),
    'toggle_view_mtime'      : lambda: pyful.filer.toggle_view_mtime(),

    'sort_name'     : lambda: pyful.filer.dir.sort_name(),
    'sort_name_rev' : lambda: pyful.filer.dir.sort_name_rev(),
    'sort_ext'      : lambda: pyful.filer.dir.sort_ext(),
    'sort_ext_rev'  : lambda: pyful.filer.dir.sort_ext_rev(),
    'sort_size'     : lambda: pyful.filer.dir.sort_size(),
    'sort_size_rev' : lambda: pyful.filer.dir.sort_size_rev(),
    'sort_time'     : lambda: pyful.filer.dir.sort_time(),
    'sort_time_rev' : lambda: pyful.filer.dir.sort_time_rev(),
    'sort_nlink'    : lambda: pyful.filer.dir.sort_nlink(),
    'sort_nlink_rev': lambda: pyful.filer.dir.sort_nlink_rev(),
    'sort_permission'     : lambda: pyful.filer.dir.sort_permission(),
    'sort_permission_rev' : lambda: pyful.filer.dir.sort_permission_rev(),

    'mark_all'     : lambda: pyful.filer.dir.mark_all('all'),
    'mark_file'    : lambda: pyful.filer.dir.mark_all('file'),
    'mark_dir'     : lambda: pyful.filer.dir.mark_all('directory'),
    'mark_symlink' : lambda: pyful.filer.dir.mark_all('symlink'),
    'mark_exec'    : lambda: pyful.filer.dir.mark_all('executable'),
    'mark_socket'  : lambda: pyful.filer.dir.mark_all('socket'),
    'mark_fifo'    : lambda: pyful.filer.dir.mark_all('fifo'),
    'mark_chr'     : lambda: pyful.filer.dir.mark_all('chr'),
    'mark_block'   : lambda: pyful.filer.dir.mark_all('block'),
    'mark_toggle'  : lambda: pyful.filer.dir.mark_toggle(),
    'mark_toggle_all': lambda: pyful.filer.dir.mark_toggle_all(),
    'mark_clear'   : lambda: pyful.filer.dir.mark_clear(),
    'mark_source'  : lambda: pyful.filer.dir.mark(_source_filter),
    'mark_archive' : lambda: pyful.filer.dir.mark(_archive_filter),
    'mark_image'   : lambda: pyful.filer.dir.mark(_image_filter),
    'mark_music'   : lambda: pyful.filer.dir.mark(_music_filter),
    'mark_video'   : lambda: pyful.filer.dir.mark(_video_filter),

    'mask_clear'   : lambda: pyful.filer.dir.mask(None),
    'mask_source'  : lambda: pyful.filer.dir.mask(_source_filter),
    'mask_archive' : lambda: pyful.filer.dir.mask(_archive_filter),
    'mask_image'   : lambda: pyful.filer.dir.mask(_image_filter),
    'mask_music'   : lambda: pyful.filer.dir.mask(_music_filter),
    'mask_video'   : lambda: pyful.filer.dir.mask(_video_filter),
    }

def _spawn_editor():
    try:
        editor = pyful.environs['EDITOR']
    except KeyError:
        editor = 'vim'
    process.spawn(editor+' %f')

def _spawn_shell():
    try:
        shell = pyful.environs['SHELL']
    except KeyError:
        shell = '/bin/bash'
    process.spawn(shell, shell)

def _exit():
    ret =  pyful.message.confirm('Exit?', ['Yes', 'No'])
    if ret == 'Yes':
        if pyful.message.timer:
            pyful.message.timer.cancel()
        sys.exit(0)

def _switch_workspace():
    titles = [w.title for w in pyful.filer.workspaces]
    pos = pyful.filer.cursor
    ret = pyful.message.confirm('Switch workspace:', options=titles, position=pos)
    for i, w in enumerate(pyful.filer.workspaces):
        if w.title == ret:
            pyful.filer.focus_workspace(i)
            break

def _drivejump():
    pyful.menu.items['Drives'] = {}
    li = []
    for i, f in enumerate(glob.glob('/media/*')+glob.glob('/mnt/*')):
        def _wrap(path):
            return lambda: pyful.filer.dir.chdir(path)
        num = str(i+1)
        li.append(('(%s) %s' % (num, f), ord(num), _wrap(f)))
    pyful.menu.items['Drives'] = li
    pyful.menu.show('Drives')

def _fileviewer():
    ext = util.extname(pyful.filer.file.name)
    pager = pyful.environs['PAGER']
    if ".gz" == ext:
        process.spawn("tar tvfz %f | "+ pager)
    elif ".tgz" == ext:
        process.spawn("tar tvfz %f | "+ pager)
    elif ".bz2" == ext:
        process.spawn("tar tvfj %f | "+ pager)
    elif ".tar" == ext:
        process.spawn("tar tvf %f | "+ pager)
    elif ".zip" == ext:
        process.spawn("zipinfo %f | "+ pager)
    elif ".rar" == ext:
        process.spawn("unrar l %f | "+ pager)
    elif ".7z"  == ext:
        process.spawn("7z l %f | "+ pager)
    else:
        process.spawn(pager+" %f")

def _pack():
    ret = pyful.message.confirm("Pack type:", ["zip", "tgz", "bz2", "tar", "rar"])
    if "zip" == ret:
        _zip()
    elif ret == "tgz":
        _tar('gzip')
    elif ret == "bz2":
        _tar('bzip2')
    elif ret == "tar":
        _tar('tar')
    elif ret == "rar":
        pyful.cmdline.start(mode.Shell(), "rar u %D2.rar %m", -7)

def _unpack():
    ext = util.extname(pyful.filer.file.name)
    if ext == ".gz":
        pyful.cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".tgz":
        pyful.cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".bz2":
        pyful.cmdline.start(mode.Shell(), "tar xvfj %f -C %D2")
    elif ext == ".tar":
        pyful.cmdline.start(mode.Shell(), "tar xvf %f -C %D2")
    elif ext == ".rar":
        pyful.cmdline.start(mode.Shell(), "rar x %f -C %D2")
    elif ext == ".zip":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".xpi":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".jar":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D2")

def _unpack2():
    ext = util.extname(pyful.filer.file.name)
    if ext == ".gz" :
        pyful.cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".tgz":
        pyful.cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".bz2":
        pyful.cmdline.start(mode.Shell(), "tar xvfj %f -C %D")
    elif ext == ".tar":
        pyful.cmdline.start(mode.Shell(), "tar xvf %f -C %D")
    elif ext == ".rar":
        pyful.cmdline.start(mode.Shell(), "rar x %f -C %D")
    elif ext == ".zip":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".xpi":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".jar":
        pyful.cmdline.start(mode.Shell(), "unzip %f -d %D")

def _change_workspace_layout():
    ret =  pyful.message.confirm("Layout:", ["tile", "tilerevese", "oneline", "onecolumn", "fullscreen"])
    if "tile" == ret:
        pyful.filer.workspace.tile()
    elif "tilerevese" == ret:
        pyful.filer.workspace.tile(reverse=True)
    elif "oneline" == ret:
        pyful.filer.workspace.oneline()
    elif "onecolumn" == ret:
        pyful.filer.workspace.onecolumn()
    elif "fullscreen" == ret:
        pyful.filer.workspace.fullscreen()

def _copy():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Copy(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.Copy(), pyful.filer.file.name)

def _delete():
    if pyful.filer.dir.ismark():
        mfiles = pyful.filer.dir.get_mark_files()
        ret = pyful.message.confirm("Delete mark files? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return
        for f in mfiles:
            filectrl.delete(f)

        pyful.filer.dir.mark_clear()
        pyful.filer.workspace.all_reload()
    else:
        pyful.cmdline.start(mode.Delete(), pyful.filer.file.name)

def _move():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Move(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.Move(), pyful.filer.file.name)

def _link():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Link(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.Link(), pyful.filer.file.name)

def _rename():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Replace(), "")
    else:
        pyful.cmdline.start(mode.Rename(), pyful.filer.file.name, -len(util.extname(pyful.filer.file.name)))

def _symlink():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Symlink(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.Symlink(), pyful.filer.file.name)

def _trashbox():
    trashbox = os.path.expanduser(pyful.environs['TRASHBOX'])
    if not os.path.exists(trashbox):
        if "Yes" == pyful.message.confirm("Trashbox doesn't exist. Make trashbox? (%s):" % trashbox, ["No", "Yes"]):
            try:
                os.makedirs(trashbox)
            except EnvironmentError as e:
                return pyful.message.error(str(e))
        else:
            return

    if pyful.filer.dir.ismark():
        mfiles = pyful.filer.dir.get_mark_files()
        ret = pyful.message.confirm("Move mark files to trashbox? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return

        for f in mfiles:
            filectrl.move(f, trashbox)
        pyful.filer.dir.mark_clear()
        pyful.filer.workspace.all_reload()
    else:
        pyful.cmdline.start(mode.TrashBox(), pyful.filer.file.name)

def _tar(tarmode=None):
    if tarmode is None:
        tarmode = pyful.message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return

    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Tar(tarmode), '')
    else:
        pyful.cmdline.start(mode.Tar(tarmode), pyful.filer.file.name)

def _tareach(tarmode=None):
    if tarmode is None:
        tarmode = pyful.message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return
    pyful.cmdline.start(mode.Tar(tarmode, each=True), '')

def _untar():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.UnTar(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.UnTar(), pyful.filer.file.name)

def _zip():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.Zip(), '')
    else:
        pyful.cmdline.start(mode.Zip(), pyful.filer.file.name)

def _zipeach():
    pyful.cmdline.start(mode.Zip(each=True), '')

def _unzip():
    if pyful.filer.dir.ismark():
        pyful.cmdline.start(mode.UnZip(), pyful.filer.workspace.nextdir.path)
    else:
        pyful.cmdline.start(mode.UnZip(), pyful.filer.file.name)
