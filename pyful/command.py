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

from pyful import Pyful
from pyful import mode
from pyful import util
from pyful import ui
from pyful import filectrl
from pyful import process

core = Pyful()

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
    'chdir'    : lambda: core.cmdline.start(mode.Chdir(), core.filer.dir.path),
    'chmod'    : lambda: core.cmdline.start(mode.Chmod(), ''),
    'chown'    : lambda: core.cmdline.start(mode.Chown(), ''),
    'glob'     : lambda: core.cmdline.start(mode.Glob(), ''),
    'globdir'  : lambda: core.cmdline.start(mode.GlobDir(), ''),
    'mark'     : lambda: core.cmdline.start(mode.Mark(), ''),
    'mask'     : lambda: core.cmdline.start(mode.Mask(), ''),
    'menu'     : lambda: core.cmdline.start(mode.Menu(), ''),
    'mkdir'    : lambda: core.cmdline.start(mode.Mkdir(), ''),
    'replace'  : lambda: core.cmdline.start(mode.Replace(), ''),
    'newfile'  : lambda: core.cmdline.start(mode.Newfile(), ''),
    'utime'    : lambda: core.cmdline.start(mode.Utime(), core.filer.file.name),
    'shell'    : lambda: core.cmdline.start(mode.Shell(), ''),
    'eval'     : lambda: core.cmdline.start(mode.Eval(), ''),
    'mx'       : lambda: core.cmdline.start(mode.Mx(), ''),

    'open_at_system' : lambda: _open_at_system(),
    'open_listfile'  : lambda: core.cmdline.start(mode.OpenListfile(), ''),
    'zoom_infobox'       : lambda: core.cmdline.start(mode.ZoomInfoBox(), ''),
    'zoom_in_infobox'    : lambda: ui.zoom_infobox(ui.InfoBox.zoom+5),
    'zoom_out_infobox'   : lambda: ui.zoom_infobox(ui.InfoBox.zoom-5),
    'zoom_normal_infobox': lambda: ui.zoom_infobox(0),
    'google_search'  : lambda: core.cmdline.start(mode.WebSearch('Google'), ''),
    'kill_thread'    : lambda: filectrl.kill_thread(),
    'drivejump'      : lambda: _drivejump(),
    'fileviewer'     : lambda: _fileviewer(),
    'pack'           : lambda: _pack(),
    'unpack'         : lambda: _unpack(),
    'unpack2'        : lambda: _unpack2(),
    'spawn_editor'   : lambda: _spawn_editor(),
    'spawn_shell'    : lambda: _spawn_shell(),
    'spawn_terminal' : lambda: _spawn_terminal(),
    'exit'           : lambda: _exit(),

    'reload_rcfile'  : lambda: core.load_rcfile(),
    'refresh_window' : lambda: core.refresh(),
    'rehash_programs': lambda: core.cmdline.completion.loadprograms(),

    'enter_mark': lambda: core.cmdline.start(mode.Shell(), ' %m', 1),
    'enter_exec': lambda: core.cmdline.start(mode.Shell(), ' ./%f', 1),
    'enter_dir' : lambda: core.filer.dir.enter_dir(),
    'enter_link': lambda: core.filer.dir.enter_link(),
    'enter_listfile': lambda: core.filer.dir.open_listfile(core.filer.file.name),

    'chdir_parent'   : lambda: core.filer.dir.chdir(os.pardir),
    'chdir_root'     : lambda: core.filer.dir.chdir('/'),
    'chdir_home'     : lambda: core.filer.dir.chdir(os.environ['HOME']),
    'chdir_neighbor' : lambda: core.filer.dir.chdir(core.filer.workspace.nextdir.path),
    'chdir_backward' : lambda: core.filer.dir.pathhistory_backward(),
    'chdir_forward'  : lambda: core.filer.dir.pathhistory_forward(),
    'finder_start'   : lambda: core.filer.finder.start(),

    'layout_tile'      : lambda: core.filer.workspace.tile(),
    'layout_tile_rev'  : lambda: core.filer.workspace.tile(reverse=True),
    'layout_oneline'   : lambda: core.filer.workspace.oneline(),
    'layout_onecolumn' : lambda: core.filer.workspace.onecolumn(),
    'layout_fullscreen': lambda: core.filer.workspace.fullscreen(),

    'switch_workspace'        : lambda: _switch_workspace(),
    'create_workspace'        : lambda: core.cmdline.start(mode.CreateWorkspace(), ''),
    'close_workspace'         : lambda: core.filer.close_workspace(),
    'change_workspace_title'  : lambda: core.cmdline.start(mode.ChangeWorkspaceTitle(), ""),
    'change_workspace_layout' : lambda: _change_workspace_layout(),
    'view_next_workspace'     : lambda: core.filer.next_workspace(),
    'view_prev_workspace'     : lambda: core.filer.prev_workspace(),
    'swap_workspace_inc'      : lambda: core.filer.swap_workspace_inc(),
    'swap_workspace_dec'      : lambda: core.filer.swap_workspace_dec(),

    'create_dir'      : lambda: core.filer.workspace.create_dir(),
    'close_dir'       : lambda: core.filer.workspace.close_dir(),
    'all_reload'      : lambda: core.filer.workspace.all_reload(),
    'swap_dir_inc'    : lambda: core.filer.workspace.swap_dir_inc(),
    'swap_dir_dec'    : lambda: core.filer.workspace.swap_dir_dec(),
    'focus_next_dir'  : lambda: core.filer.workspace.mvcursor(+1),
    'focus_prev_dir'  : lambda: core.filer.workspace.mvcursor(-1),

    'filer_cursor_down' : lambda: core.filer.dir.mvcursor(+1),
    'filer_cursor_up'   : lambda: core.filer.dir.mvcursor(-1),
    'filer_pagedown'    : lambda: core.filer.dir.pagedown(),
    'filer_pageup'      : lambda: core.filer.dir.pageup(),
    'filer_settop'      : lambda: core.filer.dir.settop(),
    'filer_setbottom'   : lambda: core.filer.dir.setbottom(),
    'filer_reset'       : lambda: core.filer.dir.reset(),

    'toggle_view_ext'        : lambda: core.filer.toggle_view_ext(),
    'toggle_view_permission' : lambda: core.filer.toggle_view_permission(),
    'toggle_view_nlink'      : lambda: core.filer.toggle_view_nlink(),
    'toggle_view_user'       : lambda: core.filer.toggle_view_user(),
    'toggle_view_group'      : lambda: core.filer.toggle_view_group(),
    'toggle_view_size'       : lambda: core.filer.toggle_view_size(),
    'toggle_view_mtime'      : lambda: core.filer.toggle_view_mtime(),

    'sort_name'     : lambda: core.filer.dir.sort_name(),
    'sort_name_rev' : lambda: core.filer.dir.sort_name_rev(),
    'sort_ext'      : lambda: core.filer.dir.sort_ext(),
    'sort_ext_rev'  : lambda: core.filer.dir.sort_ext_rev(),
    'sort_size'     : lambda: core.filer.dir.sort_size(),
    'sort_size_rev' : lambda: core.filer.dir.sort_size_rev(),
    'sort_time'     : lambda: core.filer.dir.sort_time(),
    'sort_time_rev' : lambda: core.filer.dir.sort_time_rev(),
    'sort_nlink'    : lambda: core.filer.dir.sort_nlink(),
    'sort_nlink_rev': lambda: core.filer.dir.sort_nlink_rev(),
    'sort_permission'     : lambda: core.filer.dir.sort_permission(),
    'sort_permission_rev' : lambda: core.filer.dir.sort_permission_rev(),

    'mark_all'     : lambda: core.filer.dir.mark_all('all'),
    'mark_file'    : lambda: core.filer.dir.mark_all('file'),
    'mark_dir'     : lambda: core.filer.dir.mark_all('directory'),
    'mark_symlink' : lambda: core.filer.dir.mark_all('symlink'),
    'mark_exec'    : lambda: core.filer.dir.mark_all('executable'),
    'mark_socket'  : lambda: core.filer.dir.mark_all('socket'),
    'mark_fifo'    : lambda: core.filer.dir.mark_all('fifo'),
    'mark_chr'     : lambda: core.filer.dir.mark_all('chr'),
    'mark_block'   : lambda: core.filer.dir.mark_all('block'),
    'mark_all_bcursor'     : lambda: core.filer.dir.mark_below_cursor('all'),
    'mark_file_bcursor'    : lambda: core.filer.dir.mark_below_cursor('file'),
    'mark_dir_bcursor'     : lambda: core.filer.dir.mark_below_cursor('directory'),
    'mark_symlink_bcursor' : lambda: core.filer.dir.mark_below_cursor('symlink'),
    'mark_exec_bcursor'    : lambda: core.filer.dir.mark_below_cursor('executable'),
    'mark_socket_bcursor'  : lambda: core.filer.dir.mark_below_cursor('socket'),
    'mark_fifo_bcursor'    : lambda: core.filer.dir.mark_below_cursor('fifo'),
    'mark_chr_bcursor'     : lambda: core.filer.dir.mark_below_cursor('chr'),
    'mark_block_bcursor'   : lambda: core.filer.dir.mark_below_cursor('block'),
    'mark_toggle'  : lambda: core.filer.dir.mark_toggle(),
    'mark_toggle_all': lambda: core.filer.dir.mark_toggle_all(),
    'mark_clear'   : lambda: core.filer.dir.mark_clear(),
    'mark_source'  : lambda: core.filer.dir.mark(_source_filter),
    'mark_archive' : lambda: core.filer.dir.mark(_archive_filter),
    'mark_image'   : lambda: core.filer.dir.mark(_image_filter),
    'mark_music'   : lambda: core.filer.dir.mark(_music_filter),
    'mark_video'   : lambda: core.filer.dir.mark(_video_filter),

    'mask_clear'   : lambda: core.filer.dir.mask(None),
    'mask_source'  : lambda: core.filer.dir.mask(_source_filter),
    'mask_archive' : lambda: core.filer.dir.mask(_archive_filter),
    'mask_image'   : lambda: core.filer.dir.mask(_image_filter),
    'mask_music'   : lambda: core.filer.dir.mask(_music_filter),
    'mask_video'   : lambda: core.filer.dir.mask(_video_filter),
    }

def _open_at_system():
    try:
        if core.environs['PLATFORM'] == 'cygwin':
            process.spawn("cygstart %f %&")
        else:
            process.spawn("xdg-open %f %&")
    except Exception as e:
        core.message.exception(e)

def _spawn_editor():
    try:
        editor = core.environs['EDITOR']
    except KeyError:
        editor = 'vim'
    process.spawn(editor+' %f')

def _spawn_shell():
    try:
        shell = core.environs['SHELL']
    except KeyError:
        shell = '/bin/bash'
    process.spawn(shell, shell)

def _spawn_terminal():
    try:
        process.spawn(process.Process.terminal_emulator[0]+' %&')
    except Exception as e:
        core.message.exception(e)

def _exit():
    ret =  core.message.confirm('Exit?', ['Yes', 'No'])
    if ret == 'Yes':
        if core.message.timer:
            core.message.timer.cancel()
        sys.exit(0)

def _switch_workspace():
    titles = [w.title for w in core.filer.workspaces]
    pos = core.filer.cursor
    ret = core.message.confirm('Switch workspace:', options=titles, position=pos)
    for i, w in enumerate(core.filer.workspaces):
        if w.title == ret:
            core.filer.focus_workspace(i)
            break

def _drivejump():
    core.menu.items['Drives'] = {}
    li = []
    for i, f in enumerate(glob.glob('/media/*')+glob.glob('/mnt/*')):
        def _wrap(path):
            return lambda: core.filer.dir.chdir(path)
        num = str(i+1)
        li.append(('(%s) %s' % (num, f), ord(num), _wrap(f)))
    core.menu.items['Drives'] = li
    core.menu.show('Drives')

def _fileviewer():
    ext = util.extname(core.filer.file.name)
    pager = core.environs['PAGER']
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
    ret = core.message.confirm("Pack type:", ["zip", "tgz", "bz2", "tar", "rar"])
    if "zip" == ret:
        _zip()
    elif ret == "tgz":
        _tar('gzip')
    elif ret == "bz2":
        _tar('bzip2')
    elif ret == "tar":
        _tar('tar')
    elif ret == "rar":
        core.cmdline.start(mode.Shell(), "rar u %D2.rar %m", -7)

def _unpack():
    ext = util.extname(core.filer.file.name)
    if ext == ".gz":
        core.cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".tgz":
        core.cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".bz2":
        core.cmdline.start(mode.Shell(), "tar xvfj %f -C %D2")
    elif ext == ".tar":
        core.cmdline.start(mode.Shell(), "tar xvf %f -C %D2")
    elif ext == ".rar":
        core.cmdline.start(mode.Shell(), "rar x %f -C %D2")
    elif ext == ".zip":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".xpi":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".jar":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D2")

def _unpack2():
    ext = util.extname(core.filer.file.name)
    if ext == ".gz" :
        core.cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".tgz":
        core.cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".bz2":
        core.cmdline.start(mode.Shell(), "tar xvfj %f -C %D")
    elif ext == ".tar":
        core.cmdline.start(mode.Shell(), "tar xvf %f -C %D")
    elif ext == ".rar":
        core.cmdline.start(mode.Shell(), "rar x %f -C %D")
    elif ext == ".zip":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".xpi":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".jar":
        core.cmdline.start(mode.Shell(), "unzip %f -d %D")

def _change_workspace_layout():
    ret =  core.message.confirm("Layout:", ["tile", "tilerevese", "oneline", "onecolumn", "fullscreen"])
    if "tile" == ret:
        core.filer.workspace.tile()
    elif "tilerevese" == ret:
        core.filer.workspace.tile(reverse=True)
    elif "oneline" == ret:
        core.filer.workspace.oneline()
    elif "onecolumn" == ret:
        core.filer.workspace.onecolumn()
    elif "fullscreen" == ret:
        core.filer.workspace.fullscreen()

def _copy():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Copy(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.Copy(), core.filer.file.name)

def _delete():
    if core.filer.dir.ismark():
        mfiles = core.filer.dir.get_mark_files()
        ret = core.message.confirm("Delete mark files? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return
        for f in mfiles:
            filectrl.delete(f)

        core.filer.dir.mark_clear()
        core.filer.workspace.all_reload()
    else:
        core.cmdline.start(mode.Delete(), core.filer.file.name)

def _move():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Move(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.Move(), core.filer.file.name)

def _link():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Link(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.Link(), core.filer.file.name)

def _rename():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Replace(), "")
    else:
        core.cmdline.start(mode.Rename(), core.filer.file.name, -len(util.extname(core.filer.file.name)))

def _symlink():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Symlink(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.Symlink(), core.filer.file.name)

def _trashbox():
    trashbox = os.path.expanduser(core.environs['TRASHBOX'])
    if not os.path.exists(trashbox):
        if "Yes" == core.message.confirm("Trashbox doesn't exist. Make trashbox? (%s):" % trashbox, ["No", "Yes"]):
            try:
                os.makedirs(trashbox)
            except EnvironmentError as e:
                return core.message.error(str(e))
        else:
            return

    if core.filer.dir.ismark():
        mfiles = core.filer.dir.get_mark_files()
        ret = core.message.confirm("Move mark files to trashbox? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return

        for f in mfiles:
            filectrl.move(f, trashbox)
        core.filer.dir.mark_clear()
        core.filer.workspace.all_reload()
    else:
        core.cmdline.start(mode.TrashBox(), core.filer.file.name)

def _tar(tarmode=None):
    if tarmode is None:
        tarmode = core.message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return

    if core.filer.dir.ismark():
        core.cmdline.start(mode.Tar(tarmode), '')
    else:
        core.cmdline.start(mode.Tar(tarmode), core.filer.file.name)

def _tareach(tarmode=None):
    if tarmode is None:
        tarmode = core.message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return
    core.cmdline.start(mode.Tar(tarmode, each=True), '')

def _untar():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.UnTar(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.UnTar(), core.filer.file.name)

def _zip():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.Zip(), '')
    else:
        core.cmdline.start(mode.Zip(), core.filer.file.name)

def _zipeach():
    core.cmdline.start(mode.Zip(each=True), '')

def _unzip():
    if core.filer.dir.ismark():
        core.cmdline.start(mode.UnZip(), core.filer.workspace.nextdir.path)
    else:
        core.cmdline.start(mode.UnZip(), core.filer.file.name)
