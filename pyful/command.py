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

commands = {}

def defcmd(name, doc, cmd):
    cmd.__doc__ = doc
    commands.update({name: cmd})

_image_filter = re.compile('\.(jpe?g|gif|png|bmp|tiff|jp2|j2c|svg|eps)$')
_music_filter = re.compile('\.(ogg|mp3|flac|ape|tta|tak|mid|wma|wav)$')
_video_filter = re.compile('\.(avi|mkv|mp4|mpe?g|wmv|asf|rm|ram|ra)$')
_archive_filter = re.compile('\.(zip|rar|lzh|cab|tar|7z|gz|bz2|xz|taz|tgz|tbz|txz|yz2)$')
_source_filter = re.compile('\.(py|rb|hs|el|js|lua|java|c|cc|cpp|cs|pl|php)$')

defcmd('reload_rcfile',
       """Reload %s""" % Pyful.environs['RCFILE'],
       lambda: _reload_rcfile())

defcmd('refresh_window',
       """Refresh all window.""",
       lambda: ui.refresh())

defcmd('rehash_programs',
       """Rehash of programs from PATH.
       PATH your environment is as follows:
       %s
       """ % os.linesep.join(['* '+path for path in os.environ['PATH'].split(os.pathsep)]),
       lambda: ui.getcomponent('Cmdline').completion.loadprograms())

defcmd('open_at_system',
       """Open the file under cursor at the file association of system.
       * Linux distributions -> 'xdg-open'
       * Cygwin -> 'cygstart'
       """,
       lambda: _open_at_system())

defcmd('spawn_editor',
       """Spawn the editor registered in Pyful.environs['EDITOR']""",
       lambda: _spawn_editor())

defcmd('spawn_shell',
       """Spawn the shell registered in pyful.process.Process.shell""",
       lambda: _spawn_shell())

defcmd('spawn_terminal',
       """Spawn the terminal registered in pyful.process.Process.terminal_emulator""",
       lambda: _spawn_terminal())

defcmd('exit',
       """Termination of application.""",
       lambda: _exit())

defcmd('finder_start',
       """Start finder of focused directory.""",
       lambda: ui.getcomponent('Filer').finder.start())

defcmd('help',
       """Invoke command line of help mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Help(), ''))

defcmd('help_all',
       """Show all command's help.""",
       lambda: ui.getcomponent("Help").show_all_command())

defcmd('change_looks',
       """Changing look and feel of pyful.
       There is the following kinds of looks:
       * default
       * midnight
       * dark
       * light\n
       Present looks is preserved in Pyful.environs['LOOKS'].
       The setting concerning looks consults the pyful.look module.
       """,
       lambda: ui.getcomponent('Cmdline').start(mode.ChangeLooks(), ''))

defcmd('google_search',
       """Search word in google on the regulated web browser.""",
       lambda: ui.getcomponent('Cmdline').start(mode.WebSearch('Google'), ''))

defcmd('open_listfile',
       """Invoke command line of open list file mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.OpenListfile(), ''))

defcmd('zoom_infobox',
       """Invoke command line of zoom infobox mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.ZoomInfoBox(), ''))

defcmd('zoom_in_infobox',
       """Zoom in of infobox.""",
       lambda: ui.zoom_infobox(ui.InfoBox.zoom+5))

defcmd('zoom_out_infobox',
       """Zoom out of infobox.""",
       lambda: ui.zoom_infobox(ui.InfoBox.zoom-5))

defcmd('zoom_normal_infobox',
       """Set zoom to default value.""",
       lambda: ui.zoom_infobox(0))

defcmd('message_history',
       """Display message history.""",
       lambda: message.viewhistroy())

defcmd('kill_thread',
       """Kill of a job threads.""",
       lambda: filectrl.kill_thread())

defcmd('drivejump',
       """Display the menu of an external disk where mount was done.""",
       lambda: _drivejump())

defcmd('fileviewer',
       """File view by tar, zipinfo, unrar, 7z and Pyful.environs['PAGER'].""",
       lambda: _fileviewer())

defcmd('pack',
       """File pack by tar, zip and rar.""",
       lambda: _pack())

defcmd('unpack',
       """Unpack file of tar, zip and rar to neighbor directory.""",
       lambda: _unpack())

defcmd('unpack2',
       """Unpack file of tar, zip and rar to current directory.""",
       lambda: _unpack2())

defcmd('enter_mark',
       """Behavior of mark files.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Shell(), ' %m', 1))

defcmd('enter_exec',
       """Behavior of executable file.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Shell(), ' ./%f', 1))

defcmd('enter_dir',
       """Behavior of directory.""",
       lambda: ui.getcomponent('Filer').dir.enter_dir())

defcmd('enter_link',
       """Behavior of symlink.""",
       lambda: ui.getcomponent('Filer').dir.enter_link())

defcmd('enter_listfile',
       """Behavior of list file.
       list file is a file to which the absolute path is written and extension is '.list'.
       """,
       lambda: ui.getcomponent('Filer').dir.open_listfile(ui.getcomponent('Filer').file.name))

defcmd('switch_workspace',
       """Switching workspaces.""",
       lambda: _switch_workspace())

defcmd('create_workspace',
       """Create new workspace.""",
       lambda: ui.getcomponent('Cmdline').start(mode.CreateWorkspace(), ''))

defcmd('close_workspace',
       """Close current workspace.""",
       lambda: ui.getcomponent('Filer').close_workspace())

defcmd('change_workspace_title',
       """Change current workspace's title.""",
       lambda: ui.getcomponent('Cmdline').start(mode.ChangeWorkspaceTitle(), ""))

defcmd('change_workspace_layout',
       """Change current workspace's layout.
       Layouts are following kinds:
       * Tile
       * Tile of reverse
       * Oneline
       * Onecolumn
       * Fullscreen
       """,
       lambda: _change_workspace_layout())

defcmd('view_next_workspace',
       """Switching to next workspace.""",
       lambda: ui.getcomponent('Filer').next_workspace())

defcmd('view_prev_workspace',
       """Switching to previous workspace.""",
       lambda: ui.getcomponent('Filer').prev_workspace())

defcmd('swap_workspace_inc',
       """Swap current workspace to next workspace.""",
       lambda: ui.getcomponent('Filer').swap_workspace_inc())

defcmd('swap_workspace_dec',
       """Swap current workspace to previous workspace.""",
       lambda: ui.getcomponent('Filer').swap_workspace_dec())

defcmd('layout_tile',
       """Change workspace layout to Tile""",
       lambda: ui.getcomponent('Filer').workspace.tile())

defcmd('layout_tile_rev',
       """Change workspace layout to Tile of reverse.""",
       lambda: ui.getcomponent('Filer').workspace.tile(reverse=True))

defcmd('layout_oneline',
       """Change workspace layout to Oneline.""",
       lambda: ui.getcomponent('Filer').workspace.oneline())

defcmd('layout_onecolumn',
       """Change workspace layout to Onecolumn.""",
       lambda: ui.getcomponent('Filer').workspace.onecolumn())

defcmd('layout_fullscreen',
       """Change workspace layout to Fullscreen.""",
       lambda: ui.getcomponent('Filer').workspace.fullscreen())

defcmd('chdir_parent',
       """Change current directory to parent directory.""",
       lambda: ui.getcomponent('Filer').dir.chdir(os.pardir))

defcmd('chdir_root',
       """Change current directory to root directory.""",
       lambda: ui.getcomponent('Filer').dir.chdir('/'))

defcmd('chdir_home',
       """Change current directory to home directory.""",
       lambda: ui.getcomponent('Filer').dir.chdir(os.environ['HOME']))

defcmd('chdir_neighbor',
       """Change current directory to neighbor directory.""",
       lambda: ui.getcomponent('Filer').dir.chdir(ui.getcomponent('Filer').workspace.nextdir.path))

defcmd('chdir_backward',
       """Change current directory to backward of directory history.""",
       lambda: ui.getcomponent('Filer').dir.pathhistory_backward())

defcmd('chdir_forward',
       """Change current directory to forward of directory history.""",
       lambda: ui.getcomponent('Filer').dir.pathhistory_forward())

defcmd('sort_name',
       """Sort name by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_name())

defcmd('sort_name_rev',
       """Sort name by descending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_name_rev())

defcmd('sort_ext',
       """Sort file extension by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_ext())

defcmd('sort_ext_rev',
       """Sort file extension by descending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_ext_rev())

defcmd('sort_size',
       """Sort file size by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_size())

defcmd('sort_size_rev',
       """Sort file size by descending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_size_rev())

defcmd('sort_time',
       """Sort time by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_time())

defcmd('sort_time_rev',
       """Sort time by descending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_time_rev())

defcmd('sort_nlink',
       """Sort link by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_nlink())

defcmd('sort_nlink_rev',
       """Sort link by descending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_nlink_rev())

defcmd('sort_permission',
       """Sort permission by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_permission())

defcmd('sort_permission_rev',
       """Sort permission by ascending order.""",
       lambda: ui.getcomponent('Filer').dir.sort_permission_rev())

defcmd('toggle_view_ext',
       """Toggle the file extension display.""",
       lambda: ui.getcomponent('Filer').toggle_view_ext())

defcmd('toggle_view_permission',
       """Toggle the file permission display.""",
       lambda: ui.getcomponent('Filer').toggle_view_permission())

defcmd('toggle_view_nlink',
       """Toggle the nuber of link display.""",
       lambda: ui.getcomponent('Filer').toggle_view_nlink())

defcmd('toggle_view_user',
       """Toggle the user name of file display.""",
       lambda: ui.getcomponent('Filer').toggle_view_user())

defcmd('toggle_view_group',
       """Toggle the group name of file display.""",
       lambda: ui.getcomponent('Filer').toggle_view_group())

defcmd('toggle_view_size',
       """Toggle the file size display.""",
       lambda: ui.getcomponent('Filer').toggle_view_size())

defcmd('toggle_view_mtime',
       """Toggle the change time of file display.""",
       lambda: ui.getcomponent('Filer').toggle_view_mtime())

defcmd('create_dir',
       """Create directory in current workspace.""",
       lambda: ui.getcomponent('Filer').workspace.create_dir())

defcmd('close_dir',
       """Close focus directory in current workspace.""",
       lambda: ui.getcomponent('Filer').workspace.close_dir())

defcmd('all_reload',
       """Reload files of current workspace directorise.""",
       lambda: ui.getcomponent('Filer').workspace.all_reload())

defcmd('swap_dir_inc',
       """Swap current directory to next directory.""",
       lambda: ui.getcomponent('Filer').workspace.swap_dir_inc())

defcmd('swap_dir_dec',
       """Swap current directory to previous directory.""",
       lambda: ui.getcomponent('Filer').workspace.swap_dir_dec())

defcmd('focus_next_dir',
       """Focus of cursor to next directory.""",
       lambda: ui.getcomponent('Filer').workspace.mvcursor(+1))

defcmd('focus_prev_dir',
       """Focus of curosr to previous directory.""",
       lambda: ui.getcomponent('Filer').workspace.mvcursor(-1))

defcmd('filer_cursor_down',
       """Cursor down in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.mvcursor(+1))

defcmd('filer_cursor_up',
       """Cursor up in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.mvcursor(-1))

defcmd('filer_pagedown',
       """Page down in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.pagedown())

defcmd('filer_pageup',
       """Page up in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.pageup())

defcmd('filer_settop',
       """Set cursor to page top in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.settop())

defcmd('filer_setbottom',
       """Set cursor to page bottom in focused directory.""",
       lambda: ui.getcomponent('Filer').dir.setbottom())

defcmd('filer_reset',
       """Reset the glob, mask and mark of focused directory.""",
       lambda: ui.getcomponent('Filer').dir.reset())

defcmd('mark_all',
       """Mark all objects in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('all'))

defcmd('mark_file',
       """Mark all files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('file'))

defcmd('mark_dir',
       """Mark all directories in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('directory'))

defcmd('mark_symlink',
       """Mark all symlinks in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('symlink'))

defcmd('mark_exec',
       """Mark all executable files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('executable'))

defcmd('mark_socket',
       """Mark all sockets in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('socket'))

defcmd('mark_fifo',
       """Mark all fifo in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('fifo'))

defcmd('mark_chr',
       """Mark all chr files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('chr'))

defcmd('mark_block',
       """Mark all block files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_all('block'))

defcmd('mark_all_bcursor',
       """Mark all objects from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('all'))

defcmd('mark_file_bcursor',
       """Mark all files from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('file'))

defcmd('mark_dir_bcursor',
       """Mark all directries from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('directory'))

defcmd('mark_symlink_bcursor',
       """Mark all symlinks from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('symlink'))

defcmd('mark_exec_bcursor',
       """Mark all executable files from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('executable'))

defcmd('mark_socket_bcursor',
       """Mark all sockets from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('socket'))

defcmd('mark_fifo_bcursor',
       """Mark all fifo from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('fifo'))

defcmd('mark_chr_bcursor',
       """Mark all chr files from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('chr'))

defcmd('mark_block_bcursor',
       """Mark all block files from cursor in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_below_cursor('block'))

defcmd('mark_toggle',
       """Toggle mark of file under the cursor.""",
       lambda: ui.getcomponent('Filer').dir.mark_toggle())

defcmd('mark_toggle_all',
       """Toggle mark of all files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_toggle_all())

defcmd('mark_clear',
       """Clear mark of all files in current directory.""",
       lambda: ui.getcomponent('Filer').dir.mark_clear())

defcmd('mark_source',
       """Mark source files in current directory.
       Regexp of filter: %s
       """ % _source_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mark(_source_filter))

defcmd('mark_archive',
       """Mark archive files in current directory.
       Regexp of filter: %s
       """ % _archive_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mark(_archive_filter))

defcmd('mark_image',
       """Mark image files in current directory.
       Regexp of filter: %s
       """ % _image_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mark(_image_filter))

defcmd('mark_music',
       """Mark music files in current directory.
       Regexp of filter: %s
       """ % _music_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mark(_music_filter))

defcmd('mark_video',
       """Mark video files in current directory.
       Regexp of filter: %s
       """ % _video_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mark(_video_filter))

defcmd('mask_clear',
       """Claer of filter.""",
       lambda: ui.getcomponent('Filer').dir.mask(None))

defcmd('mask_source',
       """Filter source files.
       Regexp of filter: %s
       """ % _source_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mask(_source_filter))

defcmd('mask_archive',
       """Filter archive files.
       Regexp of filter: %s
       """ % _archive_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mask(_archive_filter))

defcmd('mask_image',
       """Filter image files.
       Regexp of filter: %s
       """ % _image_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mask(_image_filter))

defcmd('mask_music',
       """Filter music files.
       Regexp of filter: %s
       """ % _music_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mask(_music_filter))

defcmd('mask_video',
       """Filter video files.
       Regexp of filter: %s
       """ % _video_filter.pattern,
       lambda: ui.getcomponent('Filer').dir.mask(_video_filter))

defcmd('copy',
       """Invoke command line of copy mode.
       = Example:
       File copy from ~/example/file.txt to ~/text/file.txt
       # Invoke copy mode by  +copy+  command.
       # Specify file of copy source:
       $  $Copy from:$  ~/example/file.txt
       # Specify its destination:
       $  $Copy from ~/example/file.txt to:$  ~/text/file.txt
       """,
       lambda: _copy())

defcmd('delete',
       """Invoke command line of delete mode.""",
       lambda: _delete())

defcmd('move',
       """Invoke command line of move mode.
       = Example:
       File move from ~/example/file.txt to ~/text/file.txt
       # Invoke copy mode by  +move+  command.
       # Specify file of move source:
       $  $Move from:$  ~/example/file.txt
       # Specify its destination:
       $  $Move from ~/example/file.txt to:$  ~/text/file.txt
       If EXDEV exception (device in move source and move destination is different)
       occur, after it copy from source to destination, Pyful delete source file.
       """,
       lambda: _move())

defcmd('link',
       """Invoke command line of link mode.""",
       lambda: _link())

defcmd('rename',
       """Invoke command line of rename mode.""",
       lambda: _rename())

defcmd('symlink',
       """Invoke command line of symlink mode.""",
       lambda: _symlink())

defcmd('trashbox',
       """Invoke command line of trashbox mode.""",
       lambda: _trashbox())

defcmd('tar',
       """Invoke command line of tar mode.""",
       lambda: _tar())

defcmd('tareach',
       """Invoke command line of tareach mode.""",
       lambda: _tareach())

defcmd('untar',
       """Invoke command line of untar mode.""",
       lambda: _untar())

defcmd('zip',
       """Invoke command line of zip mode.""",
       lambda: _zip())

defcmd('zipeach',
       """Invoke command line of zipeach mode.""",
       lambda: _zipeach())

defcmd('unzip',
       """Invoke command line of unzip mode.""",
       lambda: _unzip())

defcmd('chdir',
       """Invoke command line of chdir mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Chdir(), ui.getcomponent('Filer').dir.path))

defcmd('chmod',
       """Invoke command line of chmod mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Chmod(), ''))

defcmd('chown',
       """Invoke command line of chown mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Chown(), ''))

defcmd('glob',
       """Invoke command line of glob mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Glob(), ''))

defcmd('globdir',
       """Invoke command line of globdir mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.GlobDir(), ''))

defcmd('mark',
       """Invoke command line of mark mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Mark(), ''))

defcmd('mask',
       """Invoke command line of mask mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Mask(), ''))

defcmd('menu',
       """Invoke command line of menu mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Menu(), ''))

defcmd('mkdir',
       """Invoke command line of mkdir mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Mkdir(), ''))

defcmd('replace',
       """Invoke command line of replace mode.
       The replace mode renames mark files with regexp.
       = Example:
       The extension of mark files is renamed from '.py' to '.txt'
       # Invoke replace mode by  +replace+  command.
       # The match pattern specify with regexp:
       $  $Replace pattern:$  \.py$
       # Specify the replacing string:
       $  $Replace regexp \.py\$ with:$  .txt
       """,
       lambda: ui.getcomponent('Cmdline').start(mode.Replace(), ''))

defcmd('newfile',
       """Invoke command line of new file mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Newfile(), ''))

defcmd('utime',
       """Invoke command line of utime mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Utime(), ui.getcomponent('Filer').file.name))

defcmd('shell',
       """Invoke command line of shell mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Shell(), ''))

defcmd('eval',
       """Invoke command line of eval mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Eval(), ''))

defcmd('mx',
       """Invoke command line of mx mode.""",
       lambda: ui.getcomponent('Cmdline').start(mode.Mx(), ''))

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
    try:
        process.spawn(editor+' %f')
    except Exception as e:
        message.exception(e)

def _spawn_shell():
    shell = process.Process.shell[0]
    try:
        process.spawn(shell, shell)
    except Exception as e:
        message.exception(e)

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
    filer = ui.getcomponent('Filer')
    titles = [w.title for w in filer.workspaces]
    pos = filer.cursor
    ret = message.confirm('Switch workspace:', options=titles, position=pos)
    for i, w in enumerate(filer.workspaces):
        if w.title == ret:
            filer.focus_workspace(i)
            break

def _drivejump():
    menu = ui.getcomponent("Menu")
    menu.items['Drives'] = {}
    li = []
    for i, f in enumerate(glob.glob('/media/*')+glob.glob('/mnt/*')):
        def _wrap(path):
            return lambda: ui.getcomponent('Filer').dir.chdir(path)
        num = str(i+1)
        li.append(('(%s) %s' % (num, f), ord(num), _wrap(f)))
    menu.items['Drives'] = li
    menu.show('Drives')

def _fileviewer():
    ext = util.extname(ui.getcomponent('Filer').file.name)
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
        ui.getcomponent('Cmdline').start(mode.Shell(), "rar u %D2.rar %m", -7)

def _unpack():
    ext = util.extname(ui.getcomponent('Filer').file.name)
    cmdline = ui.getcomponent('Cmdline')
    if ext == ".gz":
        cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".tgz":
        cmdline.start(mode.Shell(), "tar xvfz %f -C %D2")
    elif ext == ".bz2":
        cmdline.start(mode.Shell(), "tar xvfj %f -C %D2")
    elif ext == ".tar":
        cmdline.start(mode.Shell(), "tar xvf %f -C %D2")
    elif ext == ".rar":
        cmdline.start(mode.Shell(), "rar x %f -C %D2")
    elif ext == ".zip":
        cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".xpi":
        cmdline.start(mode.Shell(), "unzip %f -d %D2")
    elif ext == ".jar":
        cmdline.start(mode.Shell(), "unzip %f -d %D2")

def _unpack2():
    ext = util.extname(ui.getcomponent('Filer').file.name)
    cmdline = ui.getcomponent('Cmdline')
    if ext == ".gz" :
        cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".tgz":
        cmdline.start(mode.Shell(), "tar xvfz %f -C %D")
    elif ext == ".bz2":
        cmdline.start(mode.Shell(), "tar xvfj %f -C %D")
    elif ext == ".tar":
        cmdline.start(mode.Shell(), "tar xvf %f -C %D")
    elif ext == ".rar":
        cmdline.start(mode.Shell(), "rar x %f -C %D")
    elif ext == ".zip":
        cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".xpi":
        cmdline.start(mode.Shell(), "unzip %f -d %D")
    elif ext == ".jar":
        cmdline.start(mode.Shell(), "unzip %f -d %D")

def _change_workspace_layout():
    ret =  message.confirm("Layout:", ["tile", "tilerevese", "oneline", "onecolumn", "fullscreen"])
    filer = ui.getcomponent('Filer')
    if "tile" == ret:
        filer.workspace.tile()
    elif "tilerevese" == ret:
        filer.workspace.tile(reverse=True)
    elif "oneline" == ret:
        filer.workspace.oneline()
    elif "onecolumn" == ret:
        filer.workspace.onecolumn()
    elif "fullscreen" == ret:
        filer.workspace.fullscreen()

def _copy():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Copy(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Copy(), filer.file.name)

def _delete():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        files = filer.dir.get_mark_files()
        ret = message.confirm("Delete mark files? ", ["No", "Yes"], files)
        if ret == "No" or ret is None:
            return
        filectrl.delete(files)
    else:
        cmdline.start(mode.Delete(), ui.getcomponent('Filer').file.name)

def _move():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Move(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Move(), filer.file.name)

def _link():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Link(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Link(), filer.file.name)

def _rename():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Replace(), "")
    else:
        cmdline.start(mode.Rename(), filer.file.name, -len(util.extname(filer.file.name)))

def _symlink():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Symlink(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Symlink(), os.path.join(filer.dir.path, filer.file.name))

def _trashbox():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    trashbox = os.path.expanduser(Pyful.environs['TRASHBOX'])
    if not os.path.exists(trashbox):
        if "Yes" == message.confirm("Trashbox doesn't exist. Make trashbox? (%s):" % trashbox, ["No", "Yes"]):
            try:
                os.makedirs(trashbox)
            except EnvironmentError as e:
                return message.error(str(e))
        else:
            return

    if filer.dir.ismark():
        mfiles = filer.dir.get_mark_files()
        ret = message.confirm("Move mark files to trashbox? ", ["No", "Yes"], mfiles)
        if ret == "No" or ret is None:
            return

        for f in mfiles:
            filectrl.move(f, trashbox)
        filer.dir.mark_clear()
        filer.workspace.all_reload()
    else:
        cmdline.start(mode.TrashBox(), filer.file.name)

def _tar(tarmode=None):
    if tarmode is None:
        tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return

    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Tar(tarmode), '')
    else:
        cmdline.start(mode.Tar(tarmode), filer.file.name)

def _tareach(tarmode=None):
    if tarmode is None:
        tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
        if tarmode is None:
            return
    ui.getcomponent('Cmdline').start(mode.Tar(tarmode, each=True), '')

def _untar():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.UnTar(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnTar(), filer.file.name)

def _zip():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.Zip(), '')
    else:
        cmdline.start(mode.Zip(), filer.file.name)

def _zipeach():
    ui.getcomponent('Cmdline').start(mode.Zip(each=True), '')

def _unzip():
    filer = ui.getcomponent('Filer')
    cmdline = ui.getcomponent('Cmdline')
    if filer.dir.ismark():
        cmdline.start(mode.UnZip(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnZip(), filer.file.name)
