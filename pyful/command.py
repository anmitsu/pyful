# command.py - pyful command management
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

import glob
import os
import re
import sys

from pyful import Pyful, loadrcfile
from pyful import filectrl
from pyful import message
from pyful import mode
from pyful import process
from pyful import ui
from pyful import util

_cmdline = ui.getcomponent("Cmdline")
_filer = ui.getcomponent("Filer")
_menu = ui.getcomponent("Menu")
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
    'chdir'    : lambda: _cmdline.start(mode.Chdir(), _filer.dir.path),
    'chmod'    : lambda: _cmdline.start(mode.Chmod(), ''),
    'chown'    : lambda: _cmdline.start(mode.Chown(), ''),
    'glob'     : lambda: _cmdline.start(mode.Glob(), ''),
    'globdir'  : lambda: _cmdline.start(mode.GlobDir(), ''),
    'mark'     : lambda: _cmdline.start(mode.Mark(), ''),
    'mask'     : lambda: _cmdline.start(mode.Mask(), ''),
    'menu'     : lambda: _cmdline.start(mode.Menu(), ''),
    'mkdir'    : lambda: _cmdline.start(mode.Mkdir(), ''),
    'replace'  : lambda: _cmdline.start(mode.Replace(), ''),
    'newfile'  : lambda: _cmdline.start(mode.Newfile(), ''),
    'utime'    : lambda: _cmdline.start(mode.Utime(), _filer.file.name),
    'shell'    : lambda: _cmdline.start(mode.Shell(), ''),
    'eval'     : lambda: _cmdline.start(mode.Eval(), ''),
    'mx'       : lambda: _cmdline.start(mode.Mx(), ''),

    'open_at_system' : lambda: _open_at_system(),
    'open_listfile'  : lambda: _cmdline.start(mode.OpenListfile(), ''),
    'change_looks'  : lambda: _cmdline.start(mode.ChangeLooks(), ''),
    'zoom_infobox'       : lambda: _cmdline.start(mode.ZoomInfoBox(), ''),
    'zoom_in_infobox'    : lambda: ui.zoom_infobox(ui.InfoBox.zoom+5),
    'zoom_out_infobox'   : lambda: ui.zoom_infobox(ui.InfoBox.zoom-5),
    'zoom_normal_infobox': lambda: ui.zoom_infobox(0),
    'google_search'  : lambda: _cmdline.start(mode.WebSearch('Google'), ''),
    'message_history': lambda: message.viewhistroy(),
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

    'reload_rcfile'  : lambda: _reload_rcfile(),
    'refresh_window' : lambda: ui.refresh(),
    'rehash_programs': lambda: _cmdline.completion.loadprograms(),

    'enter_mark': lambda: _cmdline.start(mode.Shell(), ' %m', 1),
    'enter_exec': lambda: _cmdline.start(mode.Shell(), ' ./%f', 1),
    'enter_dir' : lambda: _filer.dir.enter_dir(),
    'enter_link': lambda: _filer.dir.enter_link(),
    'enter_listfile': lambda: _filer.dir.open_listfile(_filer.file.name),

    'chdir_parent'   : lambda: _filer.dir.chdir(os.pardir),
    'chdir_root'     : lambda: _filer.dir.chdir('/'),
    'chdir_home'     : lambda: _filer.dir.chdir(os.environ['HOME']),
    'chdir_neighbor' : lambda: _filer.dir.chdir(_filer.workspace.nextdir.path),
    'chdir_backward' : lambda: _filer.dir.pathhistory_backward(),
    'chdir_forward'  : lambda: _filer.dir.pathhistory_forward(),
    'finder_start'   : lambda: _filer.finder.start(),

    'layout_tile'      : lambda: _filer.workspace.tile(),
    'layout_tile_rev'  : lambda: _filer.workspace.tile(reverse=True),
    'layout_oneline'   : lambda: _filer.workspace.oneline(),
    'layout_onecolumn' : lambda: _filer.workspace.onecolumn(),
    'layout_fullscreen': lambda: _filer.workspace.fullscreen(),

    'switch_workspace'        : lambda: _switch_workspace(),
    'create_workspace'        : lambda: _cmdline.start(mode.CreateWorkspace(), ''),
    'close_workspace'         : lambda: _filer.close_workspace(),
    'change_workspace_title'  : lambda: _cmdline.start(mode.ChangeWorkspaceTitle(), ""),
    'change_workspace_layout' : lambda: _change_workspace_layout(),
    'view_next_workspace'     : lambda: _filer.next_workspace(),
    'view_prev_workspace'     : lambda: _filer.prev_workspace(),
    'swap_workspace_inc'      : lambda: _filer.swap_workspace_inc(),
    'swap_workspace_dec'      : lambda: _filer.swap_workspace_dec(),

    'create_dir'      : lambda: _filer.workspace.create_dir(),
    'close_dir'       : lambda: _filer.workspace.close_dir(),
    'all_reload'      : lambda: _filer.workspace.all_reload(),
    'swap_dir_inc'    : lambda: _filer.workspace.swap_dir_inc(),
    'swap_dir_dec'    : lambda: _filer.workspace.swap_dir_dec(),
    'focus_next_dir'  : lambda: _filer.workspace.mvcursor(+1),
    'focus_prev_dir'  : lambda: _filer.workspace.mvcursor(-1),

    'filer_cursor_down' : lambda: _filer.dir.mvcursor(+1),
    'filer_cursor_up'   : lambda: _filer.dir.mvcursor(-1),
    'filer_pagedown'    : lambda: _filer.dir.pagedown(),
    'filer_pageup'      : lambda: _filer.dir.pageup(),
    'filer_settop'      : lambda: _filer.dir.settop(),
    'filer_setbottom'   : lambda: _filer.dir.setbottom(),
    'filer_reset'       : lambda: _filer.dir.reset(),

    'toggle_view_ext'        : lambda: _filer.toggle_view_ext(),
    'toggle_view_permission' : lambda: _filer.toggle_view_permission(),
    'toggle_view_nlink'      : lambda: _filer.toggle_view_nlink(),
    'toggle_view_user'       : lambda: _filer.toggle_view_user(),
    'toggle_view_group'      : lambda: _filer.toggle_view_group(),
    'toggle_view_size'       : lambda: _filer.toggle_view_size(),
    'toggle_view_mtime'      : lambda: _filer.toggle_view_mtime(),

    'sort_name'     : lambda: _filer.dir.sort_name(),
    'sort_name_rev' : lambda: _filer.dir.sort_name_rev(),
    'sort_ext'      : lambda: _filer.dir.sort_ext(),
    'sort_ext_rev'  : lambda: _filer.dir.sort_ext_rev(),
    'sort_size'     : lambda: _filer.dir.sort_size(),
    'sort_size_rev' : lambda: _filer.dir.sort_size_rev(),
    'sort_time'     : lambda: _filer.dir.sort_time(),
    'sort_time_rev' : lambda: _filer.dir.sort_time_rev(),
    'sort_nlink'    : lambda: _filer.dir.sort_nlink(),
    'sort_nlink_rev': lambda: _filer.dir.sort_nlink_rev(),
    'sort_permission'     : lambda: _filer.dir.sort_permission(),
    'sort_permission_rev' : lambda: _filer.dir.sort_permission_rev(),

    'mark_all'     : lambda: _filer.dir.mark_all('all'),
    'mark_file'    : lambda: _filer.dir.mark_all('file'),
    'mark_dir'     : lambda: _filer.dir.mark_all('directory'),
    'mark_symlink' : lambda: _filer.dir.mark_all('symlink'),
    'mark_exec'    : lambda: _filer.dir.mark_all('executable'),
    'mark_socket'  : lambda: _filer.dir.mark_all('socket'),
    'mark_fifo'    : lambda: _filer.dir.mark_all('fifo'),
    'mark_chr'     : lambda: _filer.dir.mark_all('chr'),
    'mark_block'   : lambda: _filer.dir.mark_all('block'),
    'mark_all_bcursor'     : lambda: _filer.dir.mark_below_cursor('all'),
    'mark_file_bcursor'    : lambda: _filer.dir.mark_below_cursor('file'),
    'mark_dir_bcursor'     : lambda: _filer.dir.mark_below_cursor('directory'),
    'mark_symlink_bcursor' : lambda: _filer.dir.mark_below_cursor('symlink'),
    'mark_exec_bcursor'    : lambda: _filer.dir.mark_below_cursor('executable'),
    'mark_socket_bcursor'  : lambda: _filer.dir.mark_below_cursor('socket'),
    'mark_fifo_bcursor'    : lambda: _filer.dir.mark_below_cursor('fifo'),
    'mark_chr_bcursor'     : lambda: _filer.dir.mark_below_cursor('chr'),
    'mark_block_bcursor'   : lambda: _filer.dir.mark_below_cursor('block'),
    'mark_toggle'  : lambda: _filer.dir.mark_toggle(),
    'mark_toggle_all': lambda: _filer.dir.mark_toggle_all(),
    'mark_clear'   : lambda: _filer.dir.mark_clear(),
    'mark_source'  : lambda: _filer.dir.mark(_source_filter),
    'mark_archive' : lambda: _filer.dir.mark(_archive_filter),
    'mark_image'   : lambda: _filer.dir.mark(_image_filter),
    'mark_music'   : lambda: _filer.dir.mark(_music_filter),
    'mark_video'   : lambda: _filer.dir.mark(_video_filter),

    'mask_clear'   : lambda: _filer.dir.mask(None),
    'mask_source'  : lambda: _filer.dir.mask(_source_filter),
    'mask_archive' : lambda: _filer.dir.mask(_archive_filter),
    'mask_image'   : lambda: _filer.dir.mask(_image_filter),
    'mask_music'   : lambda: _filer.dir.mask(_music_filter),
    'mask_video'   : lambda: _filer.dir.mask(_video_filter),
    }

def _open_at_system():
    try:
        if sys.platform == 'cygwin':
            process.spawn("cygstart %f %&")
        else:
            process.spawn("xdg-open %f %&")
    except Exception as e:
        message.exception(e)

def _spawn_editor():
    try:
        editor = Pyful.environs['EDITOR']
    except KeyError:
        editor = 'vim'
    process.spawn(editor+' %f')

def _spawn_shell():
    try:
        shell = Pyful.environs['SHELL']
    except KeyError:
        shell = '/bin/bash'
    process.spawn(shell, shell)

def _spawn_terminal():
    try:
        process.spawn(process.Process.terminal_emulator[0]+' %&')
    except Exception as e:
        message.exception(e)

def _exit():
    ret =  message.confirm('Exit?', ['Yes', 'No'])
    if ret == 'Yes':
        message.timerkill()
        sys.exit(0)

def _reload_rcfile():
    error = loadrcfile(started=False)
    if error:
        message.exception(error)
    else:
        message.puts("Reloaded: %s" % Pyful.environs['RCFILE'])

def _switch_workspace():
    titles = [w.title for w in _filer.workspaces]
    pos = _filer.cursor
    ret = message.confirm('Switch workspace:', options=titles, position=pos)
    for i, w in enumerate(_filer.workspaces):
        if w.title == ret:
            _filer.focus_workspace(i)
            break

def _drivejump():
    _menu.items['Drives'] = {}
    li = []
    for i, f in enumerate(glob.glob('/media/*')+glob.glob('/mnt/*')):
        def _wrap(path):
            return lambda: _filer.dir.chdir(path)
        num = str(i+1)
        li.append(('(%s) %s' % (num, f), ord(num), _wrap(f)))
    _menu.items['Drives'] = li
    _menu.show('Drives')

def _fileviewer():
    ext = util.extname(_filer.file.name)
    pager = Pyful.environs['PAGER']
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
    ret = message.confirm("Pack type:", ["zip", "tgz", "bz2", "tar", "rar"])
    if "zip" == ret:
        _zip()
    elif ret == "tgz":
        _tar('gzip')
    elif ret == "bz2":
        _tar('bzip2')
    elif ret == "tar":
        _tar('tar')
    elif ret == "rar":
        _cmdline.start(mode.Shell(), "rar u %D2.rar %m", -7)

def _unpack():
    ext = util.extname(_filer.file.name)
    if ext == ".gz":
        _cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".tgz":
        _cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".bz2":
        _cmdline.start(mode.Shell(), "tar xvfj %f -C %D2")
    elif ext == ".tar":
        _cmdline.start(mode.Shell(), "tar xvf %f -C %D2")
    elif ext == ".rar":
        _cmdline.start(mode.Shell(), "rar x %f -C %D2")
    elif ext == ".zip":
        _cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".xpi":
        _cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".jar":
        _cmdline.start(mode.Shell(), "unzip %f -d %D2")

def _unpack2():
    ext = util.extname(_filer.file.name)
    if ext == ".gz" :
        _cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".tgz":
        _cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".bz2":
        _cmdline.start(mode.Shell(), "tar xvfj %f -C %D")
    elif ext == ".tar":
        _cmdline.start(mode.Shell(), "tar xvf %f -C %D")
    elif ext == ".rar":
        _cmdline.start(mode.Shell(), "rar x %f -C %D")
    elif ext == ".zip":
        _cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".xpi":
        _cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".jar":
        _cmdline.start(mode.Shell(), "unzip %f -d %D")

def _change_workspace_layout():
    ret =  message.confirm("Layout:", ["tile", "tilerevese", "oneline", "onecolumn", "fullscreen"])
    if "tile" == ret:
        _filer.workspace.tile()
    elif "tilerevese" == ret:
        _filer.workspace.tile(reverse=True)
    elif "oneline" == ret:
        _filer.workspace.oneline()
    elif "onecolumn" == ret:
        _filer.workspace.onecolumn()
    elif "fullscreen" == ret:
        _filer.workspace.fullscreen()

def _copy():
    if _filer.dir.ismark():
        _cmdline.start(mode.Copy(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.Copy(), _filer.file.name)

def _delete():
    if _filer.dir.ismark():
        files = _filer.dir.get_mark_files()
        ret = message.confirm("Delete mark files? ", ["No", "Yes"], files)
        if ret == "No" or ret is None:
            return
        filectrl.delete(files)
    else:
        _cmdline.start(mode.Delete(), _filer.file.name)

def _move():
    if _filer.dir.ismark():
        _cmdline.start(mode.Move(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.Move(), _filer.file.name)

def _link():
    if _filer.dir.ismark():
        _cmdline.start(mode.Link(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.Link(), _filer.file.name)

def _rename():
    if _filer.dir.ismark():
        _cmdline.start(mode.Replace(), "")
    else:
        _cmdline.start(mode.Rename(), _filer.file.name, -len(util.extname(_filer.file.name)))

def _symlink():
    if _filer.dir.ismark():
        _cmdline.start(mode.Symlink(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.Symlink(), os.path.join(_filer.dir.path, _filer.file.name))

def _trashbox():
    trashbox = os.path.expanduser(Pyful.environs['TRASHBOX'])
    if not os.path.exists(trashbox):
        if "Yes" == message.confirm("Trashbox doesn't exist. Make trashbox? (%s):" % trashbox, ["No", "Yes"]):
            try:
                os.makedirs(trashbox)
            except EnvironmentError as e:
                return message.error(str(e))
        else:
            return

    if _filer.dir.ismark():
        mfiles = _filer.dir.get_mark_files()
        ret = message.confirm("Move mark files to trashbox? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return

        for f in mfiles:
            filectrl.move(f, trashbox)
        _filer.dir.mark_clear()
        _filer.workspace.all_reload()
    else:
        _cmdline.start(mode.TrashBox(), _filer.file.name)

def _tar(tarmode=None):
    if tarmode is None:
        tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return

    if _filer.dir.ismark():
        _cmdline.start(mode.Tar(tarmode), '')
    else:
        _cmdline.start(mode.Tar(tarmode), _filer.file.name)

def _tareach(tarmode=None):
    if tarmode is None:
        tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return
    _cmdline.start(mode.Tar(tarmode, each=True), '')

def _untar():
    if _filer.dir.ismark():
        _cmdline.start(mode.UnTar(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.UnTar(), _filer.file.name)

def _zip():
    if _filer.dir.ismark():
        _cmdline.start(mode.Zip(), '')
    else:
        _cmdline.start(mode.Zip(), _filer.file.name)

def _zipeach():
    _cmdline.start(mode.Zip(each=True), '')

def _unzip():
    if _filer.dir.ismark():
        _cmdline.start(mode.UnZip(), _filer.workspace.nextdir.path)
    else:
        _cmdline.start(mode.UnZip(), _filer.file.name)
