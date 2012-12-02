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

import os
import sys

from pyful import Pyful
from pyful import widgets
from pyful import filectrl
from pyful import message
from pyful import mode
from pyful import process
from pyful import util
from pyful import widget

commands = {}

def define_command(func):
    commands[func.__name__.strip("_")] = func
    return func

def query(name):
    return commands[name]

def run(name):
    query(name)()

# ----------------------------------------------------------------------
# Utility commands:
@define_command
def _reload_rcfile():
    """Reload Pyful.environs["RCFILE"]"""
    try:
        path = Pyful.environs["RCFILE"]
        util.loadfile(path)
        message.puts("Reloaded: {0}".format(path))
    except Exception as e:
        message.exception(e)

@define_command
def _refresh_window():
    """Refresh all window."""
    widget.refresh_all_widgets()

@define_command
def _rehash_programs():
    """Rehash of programs from PATH."""
    widgets.cmdline.completion.loadprograms()

@define_command
def _open_at_system():
    """Open the file under cursor at the file association of system.
    * Linux distributions -> "xdg-open"
    * Cygwin -> "cygstart"
    """
    try:
        if sys.platform == "cygwin":
            process.spawn("cygstart %f %&")
        else:
            process.spawn("xdg-open %f %&")
    except Exception as e:
        message.exception(e)

@define_command
def _spawn_editor():
    """Spawn the editor registered in Pyful.environs["EDITOR"]"""
    try:
        process.spawn(Pyful.environs["EDITOR"] + " %f")
    except Exception as e:
        message.exception(e)

@define_command
def _spawn_shell():
    """Spawn the shell registered in pyful.process.Process.shell"""
    shell = process.Process.shell[0]
    try:
        process.spawn(shell, shell)
    except Exception as e:
        message.exception(e)

@define_command
def _spawn_terminal():
    """Spawn the terminal registered in pyful.process.Process.terminal_emulator"""
    try:
        process.spawn(process.Process.terminal_emulator[0]+" %&")
    except Exception as e:
        message.exception(e)

@define_command
def _exit():
    """Termination of application."""
    if "Yes" == message.confirm("Exit?", ["Yes", "No"]):
        sys.exit(0)

@define_command
def _shell():
    """Invoke command line of shell mode."""
    widgets.cmdline.start(mode.Shell())

@define_command
def _eval():
    """Invoke command line of eval mode."""
    widgets.cmdline.start(mode.Eval())

@define_command
def _mx():
    """Invoke command line of mx mode."""
    widgets.cmdline.start(mode.Mx())

@define_command
def _help():
    """Invoke command line of help mode."""
    widgets.cmdline.start(mode.Help())

@define_command
def _help_all():
    """Show all command's help."""
    widgets.help.show_all_command()

@define_command
def _change_looks():
    """Changing look and feel of pyful.
    There is the following kinds of looks:
    * default
    * midnight
    * dark
    * light\n
    Present looks is preserved in look.Look.mylook.
    The setting concerning looks consults the pyful.look module.
    """
    widgets.cmdline.start(mode.ChangeLooks())

@define_command
def _google_search():
    """Search word in google on the regulated web browser."""
    widgets.cmdline.start(mode.WebSearch("Google"))

@define_command
def _open_listfile():
    """Invoke command line of open list file mode."""
    widgets.cmdline.start(mode.OpenListfile())

@define_command
def _message_history():
    """Display message history."""
    message.drawhistroy()

@define_command
def _kill_thread():
    """Kill of a job threads."""
    filectrl.kill_thread()

@define_command
def _drivejump():
    """Display the menu of an external disk where mount was done."""
    def _wrap(path):
        return lambda: widgets.filer.dir.chdir(path)
    menu = widgets.menu
    menu.items["Drives"] = []
    exdevs = ["/media", "/mnt", "/cygdrive"]
    for path in exdevs:
        try:
            files = [os.path.join(path, f) for f in os.listdir(path)
                     if os.path.isdir(os.path.join(path, f))]
        except OSError:
            continue
        for i, f in enumerate(files):
            num = str(i+1)
            title = "({0}) {1}".format(num, f)
            menu.items["Drives"].append([title, num, _wrap(f)])
    menu.show("Drives")

@define_command
def _fileviewer():
    """File view by tar, zipinfo, unrar, 7z and Pyful.environs["PAGER"]."""
    ext = util.extname(widgets.filer.file.name)
    pager = Pyful.environs["PAGER"]
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

@define_command
def _pack():
    """File pack by tar, zip and rar."""
    ret = message.confirm("Pack type:", ["zip", "tgz", "bz2", "tar", "rar"])
    if "zip" == ret:
        _zip()
    elif ret == "tgz" or ret == "bz2" or ret == "tar":
        filer = widgets.filer
        cmdline = widgets.cmdline
        if filer.dir.ismark():
            cmdline.start(mode.Tar(ret))
        else:
            cmdline.start(mode.Tar(ret), filer.file.name)
    elif ret == "rar":
        widgets.cmdline.start(mode.Shell(), "rar u %D2.rar %m", -8)

@define_command
def _unpack():
    """Unpack file of tar, zip and rar to neighbor directory."""
    ext = util.extname(widgets.filer.file.name)
    cmdline = widgets.cmdline
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

@define_command
def _unpack2():
    """Unpack file of tar, zip and rar to current directory."""
    ext = util.extname(widgets.filer.file.name)
    cmdline = widgets.cmdline
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

# ----------------------------------------------------------------------
# Filer commands:
@define_command
def _enter_mark():
    """Behavior of mark files."""
    widgets.cmdline.start(mode.Shell(), " %m", 0)

@define_command
def _enter_exec():
    """Behavior of executable file."""
    widgets.cmdline.start(mode.Shell(), util.expandmacro(" ./%f", shell=True), 0)

@define_command
def _enter_dir():
    """Behavior of directory."""
    widgets.filer.dir.enter_dir()

@define_command
def _enter_link():
    """Behavior of symlink."""
    widgets.filer.dir.enter_link()

@define_command
def _enter_listfile():
    """Behavior of list file.
    list file is a file to which the absolute path is written.
    """
    filer = widgets.filer
    filer.dir.open_listfile(filer.file.name)

@define_command
def _finder_start():
    """Start finder of focused directory."""
    widgets.filer.finder.start()

@define_command
def _switch_workspace():
    """Switching workspaces."""
    filer = widgets.filer
    titles = [w.title for w in filer.workspaces]
    pos = filer.cursor
    ret = message.confirm("Switch workspace:", options=titles, position=pos)
    for i, w in enumerate(filer.workspaces):
        if w.title == ret:
            filer.focus_workspace(i)
            break

@define_command
def _create_workspace():
    """Create new workspace."""
    widgets.cmdline.start(mode.CreateWorkspace())

@define_command
def _close_workspace():
    """Close current workspace."""
    widgets.filer.close_workspace()

@define_command
def _change_workspace_title():
    """Change current workspace's title."""
    widgets.cmdline.start(mode.ChangeWorkspaceTitle())

@define_command
def _change_workspace_layout():
    """Change current workspace's layout.
    Layouts are following kinds:
    * Tile
    * TileLeft
    * TileTop
    * TileBottom
    * Oneline
    * Onecolumn
    * Magnifier
    * Fullscreen
    """
    ret =  message.confirm(
        "Layout:", ["Tile", "TileLeft", "TileTop", "TileBottom", "Oneline", "Onecolumn", "Magnifier", "Fullscreen"])
    filer = widgets.filer
    if "Tile" == ret:
        filer.workspace.tile()
    elif "TileLeft" == ret:
        filer.workspace.tileleft()
    elif "TileTop" == ret:
        filer.workspace.tiletop()
    elif "TileBottom" == ret:
        filer.workspace.tilebottom()
    elif "Oneline" == ret:
        filer.workspace.oneline()
    elif "Onecolumn" == ret:
        filer.workspace.onecolumn()
    elif "Magnifier" == ret:
        filer.workspace.magnifier()
    elif "Fullscreen" == ret:
        filer.workspace.fullscreen()

@define_command
def _switch_next_workspace():
    """Switching to next workspace."""
    widgets.filer.next_workspace()

@define_command
def _switch_prev_workspace():
    """Switching to previous workspace."""
    widgets.filer.prev_workspace()

@define_command
def _swap_workspace_inc():
    """Swap current workspace to next workspace."""
    widgets.filer.swap_workspace_inc()

@define_command
def _swap_workspace_dec():
    """Swap current workspace to previous workspace."""
    widgets.filer.swap_workspace_dec()

@define_command
def _layout_tile():
    """Change workspace layout to Tile.
    = Preview:
    _________________________
    |           |           |
    |           |     2     |
    |     1     |___________|
    |           |           |
    |           |     3     |
    |___________|___________|
    """
    widgets.filer.workspace.tile()

@define_command
def _layout_tileleft():
    """Change workspace layout to Tile of left.
    = Preview:
    _________________________
    |           |           |
    |     2     |           |
    |___________|     1     |
    |           |           |
    |     3     |           |
    |___________|___________|
    """
    widgets.filer.workspace.tileleft()

@define_command
def _layout_tiletop():
    """Change workspace layout to Tile of top.
    = Preview:
    _________________________
    |           |           |
    |     2     |     3     |
    |___________|___________|
    |                       |
    |           1           |
    |_______________________|
    """
    widgets.filer.workspace.tiletop()

@define_command
def _layout_tilebottom():
    """Change workspace layout to Tile of bottom.
    = Preview:
    _________________________
    |                       |
    |           1           |
    |_______________________|
    |           |           |
    |     2     |     3     |
    |___________|___________|
    """
    widgets.filer.workspace.tilebottom()

@define_command
def _layout_oneline():
    """Change workspace layout to Oneline.
    = Preview:
    _________________________
    |       |       |       |
    |       |       |       |
    |   1   |   2   |   3   |
    |       |       |       |
    |       |       |       |
    |_______|_______|_______|
    """
    widgets.filer.workspace.oneline()

@define_command
def _layout_onecolumn():
    """Change workspace layout to Onecolumn.
    = Preview:
    _________________________
    |           1           |
    |_______________________|
    |           2           |
    |_______________________|
    |           3           |
    |_______________________|
    """
    widgets.filer.workspace.onecolumn()

@define_command
def _layout_magnifier():
    """Change workspace layout to Magnifier.
    = Preview:
    _________________________
    |    _______________    |
    | 2  |             |    |
    |____|      1      |____|
    |    |             |    |
    | 3  |_____________|    |
    |_______________________|
    """
    widgets.filer.workspace.magnifier()

@define_command
def _layout_fullscreen():
    """Change workspace layout to Fullscreen.
    = Preview:
    _________________________
    |                       |
    |                       |
    |        1, 2, 3        |
    |                       |
    |                       |
    |_______________________|
    """
    widgets.filer.workspace.fullscreen()

@define_command
def _chdir_parent():
    """Change current directory to parent directory."""
    widgets.filer.dir.chdir(os.pardir)

@define_command
def _chdir_root():
    """Change current directory to root directory."""
    widgets.filer.dir.chdir("/")

@define_command
def _chdir_home():
    """Change current directory to home directory."""
    widgets.filer.dir.chdir(os.getenv("HOME"))

@define_command
def _chdir_neighbor():
    """Change current directory to neighbor directory."""
    filer = widgets.filer
    filer.dir.chdir(filer.workspace.nextdir.path)

@define_command
def _chdir_backward():
    """Change current directory to backward of directory history."""
    widgets.filer.dir.history.backward()

@define_command
def _chdir_forward():
    """Change current directory to forward of directory history."""
    widgets.filer.dir.history.forward()

@define_command
def _sort_name():
    """Sort name by ascending order."""
    widgets.filer.dir.sort_name(rev=False)

@define_command
def _sort_name_rev():
    """Sort name by descending order."""
    widgets.filer.dir.sort_name(rev=True)

@define_command
def _sort_ext():
    """Sort file extension by ascending order."""
    widgets.filer.dir.sort_ext(rev=False)

@define_command
def _sort_ext_rev():
    """Sort file extension by descending order."""
    widgets.filer.dir.sort_ext(rev=True)

@define_command
def _sort_size():
    """Sort file size by ascending order."""
    widgets.filer.dir.sort_size(rev=False)

@define_command
def _sort_size_rev():
    """Sort file size by descending order."""
    widgets.filer.dir.sort_size(rev=True)

@define_command
def _sort_time():
    """Sort time by ascending order."""
    widgets.filer.dir.sort_time(rev=False)

@define_command
def _sort_time_rev():
    """Sort time by descending order."""
    widgets.filer.dir.sort_time(rev=True)

@define_command
def _sort_nlink():
    """Sort link by ascending order."""
    widgets.filer.dir.sort_nlink(rev=False)

@define_command
def _sort_nlink_rev():
    """Sort link by descending order."""
    widgets.filer.dir.sort_nlink(rev=True)

@define_command
def _sort_permission():
    """Sort permission by ascending order."""
    widgets.filer.dir.sort_permission(rev=False)

@define_command
def _sort_permission_rev():
    """Sort permission by ascending order."""
    widgets.filer.dir.sort_permission(rev=True)

@define_command
def _toggle_sort_updir():
    """Toggle of directory sort type"""
    filer = widgets.filer
    dircls = filer.dir.__class__
    dircls.sort_updir = not dircls.sort_updir
    filer.workspace.all_reload()

@define_command
def _toggle_draw_ext():
    """Toggle the file extension display."""
    widgets.filer.toggle_draw_ext()

@define_command
def _toggle_draw_permission():
    """Toggle the file permission display."""
    widgets.filer.toggle_draw_permission()

@define_command
def _toggle_draw_nlink():
    """Toggle the nuber of link display."""
    widgets.filer.toggle_draw_nlink()

@define_command
def _toggle_draw_user():
    """Toggle the user name of file display."""
    widgets.filer.toggle_draw_user()

@define_command
def _toggle_draw_group():
    """Toggle the group name of file display."""
    widgets.filer.toggle_draw_group()

@define_command
def _toggle_draw_size():
    """Toggle the file size display."""
    widgets.filer.toggle_draw_size()

@define_command
def _toggle_draw_mtime():
    """Toggle the change time of file display."""
    widgets.filer.toggle_draw_mtime()

@define_command
def _create_dir():
    """Create directory in current workspace."""
    widgets.filer.workspace.create_dir()

@define_command
def _close_dir():
    """Close focus directory in current workspace."""
    widgets.filer.workspace.close_dir()

@define_command
def _all_reload():
    """Reload files of current workspace directorise."""
    widgets.filer.workspace.all_reload()

@define_command
def _swap_dir_inc():
    """Swap current directory to next directory."""
    widgets.filer.workspace.swap_dir_inc()

@define_command
def _swap_dir_dec():
    """Swap current directory to previous directory."""
    widgets.filer.workspace.swap_dir_dec()

@define_command
def _focus_next_dir():
    """Focus of cursor to next directory."""
    widgets.filer.workspace.mvcursor(+1)

@define_command
def _focus_prev_dir():
    """Focus of curosr to previous directory."""
    widgets.filer.workspace.mvcursor(-1)

@define_command
def _filer_cursor_down():
    """Cursor down in focused directory."""
    widgets.filer.dir.mvcursor(+1)

@define_command
def _filer_cursor_up():
    """Cursor up in focused directory."""
    widgets.filer.dir.mvcursor(-1)

@define_command
def _filer_cursor_more_down():
    """Cursor more down in focused directory."""
    widgets.filer.dir.mvcursor(+5)

@define_command
def _filer_cursor_more_up():
    """Cursor more up in focused directory."""
    widgets.filer.dir.mvcursor(-5)

@define_command
def _filer_scroll_down():
    """Scroll down in focused directory."""
    widgets.filer.dir.mvscroll(+1)

@define_command
def _filer_scroll_up():
    """Scroll up in focused directory."""
    widgets.filer.dir.mvscroll(-1)

@define_command
def _filer_pagedown():
    """Page down in focused directory."""
    widgets.filer.dir.pagedown()

@define_command
def _filer_pageup():
    """Page up in focused directory."""
    widgets.filer.dir.pageup()

@define_command
def _filer_settop():
    """Set cursor to page top in focused directory."""
    widgets.filer.dir.settop()

@define_command
def _filer_setbottom():
    """Set cursor to page bottom in focused directory."""
    widgets.filer.dir.setbottom()

@define_command
def _filer_reset():
    """Reset the glob, mask and mark of focused directory."""
    widgets.filer.dir.reset()

# ----------------------------------------------------------------------
# Mark commands:
@define_command
def _mark_all():
    """Mark all objects in current directory."""
    widgets.filer.dir.mark_all("all")

@define_command
def _mark_file():
    """Mark all files in current directory."""
    widgets.filer.dir.mark_all("file")

@define_command
def _mark_dir():
    """Mark all directories in current directory."""
    widgets.filer.dir.mark_all("directory")

@define_command
def _mark_symlink():
    """Mark all symlinks in current directory."""
    widgets.filer.dir.mark_all("symlink")

@define_command
def _mark_exec():
    """Mark all executable files in current directory."""
    widgets.filer.dir.mark_all("executable")

@define_command
def _mark_socket():
    """Mark all sockets in current directory."""
    widgets.filer.dir.mark_all("socket")

@define_command
def _mark_fifo():
    """Mark all fifo in current directory."""
    widgets.filer.dir.mark_all("fifo")

@define_command
def _mark_chr():
    """Mark all chr files in current directory."""
    widgets.filer.dir.mark_all("chr")

@define_command
def _mark_block():
    """Mark all block files in current directory."""
    widgets.filer.dir.mark_all("block")

@define_command
def _mark_all_bcursor():
    """Mark all objects from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("all")

@define_command
def _mark_file_bcursor():
    """Mark all files from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("file")

@define_command
def _mark_dir_bcursor():
    """Mark all directries from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("directory")

@define_command
def _mark_symlink_bcursor():
    """Mark all symlinks from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("symlink")

@define_command
def _mark_exec_bcursor():
    """Mark all executable files from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("executable")

@define_command
def _mark_socket_bcursor():
    """Mark all sockets from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("socket")

@define_command
def _mark_fifo_bcursor():
    """Mark all fifo from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("fifo")

@define_command
def _mark_chr_bcursor():
    """Mark all chr files from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("chr")

@define_command
def _mark_block_bcursor():
    """Mark all block files from cursor in current directory."""
    widgets.filer.dir.mark_below_cursor("block")

@define_command
def _mark_toggle():
    """Toggle mark of file under the cursor."""
    widgets.filer.dir.mark_toggle()

@define_command
def _mark_toggle_all():
    """Toggle mark of all files in current directory."""
    widgets.filer.dir.mark_toggle_all()

@define_command
def _mark_clear():
    """Clear mark of all files in current directory."""
    widgets.filer.dir.mark_clear()

# ----------------------------------------------------------------------
# Mask commands:
@define_command
def _mask_clear():
    """Claer of filter."""
    widgets.filer.dir.mask(None)

# ----------------------------------------------------------------------
# File control  commands:
@define_command
def _chdir():
    """Invoke command line of chdir mode."""
    widgets.cmdline.start(mode.Chdir(), widgets.filer.dir.path)

@define_command
def _chmod():
    """Invoke command line of chmod mode."""
    widgets.cmdline.start(mode.Chmod())

@define_command
def _chown():
    """Invoke command line of chown mode."""
    widgets.cmdline.start(mode.Chown())

@define_command
def _copy():
    """Invoke command line of copy mode.
    = Example:
    File copy from ~/example/file.txt to ~/text/file.txt
    # Invoke copy mode by  +copy+  command.
    # Specify file of copy source:
    $  $Copy from:$  ~/example/file.txt
    # Specify its destination:
    $  $Copy from ~/example/file.txt to:$  ~/text/file.txt
    """
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Copy(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Copy(), filer.file.name)

@define_command
def _delete():
    """Invoke command line of delete mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        files = filer.dir.get_mark_files()
        ret = message.confirm("Delete mark files? ", ["No", "Yes"], files)
        if ret == "No" or ret is None:
            return
        filectrl.delete(files)
    else:
        cmdline.start(mode.Delete(), filer.file.name)

@define_command
def _glob():
    """Invoke command line of glob mode."""
    widgets.cmdline.start(mode.Glob())

@define_command
def _globdir():
    """Invoke command line of globdir mode."""
    widgets.cmdline.start(mode.GlobDir())

@define_command
def _link():
    """Invoke command line of link mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Link(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Link(), filer.file.name)

@define_command
def _mark():
    """Invoke command line of mark mode."""
    widgets.cmdline.start(mode.Mark())

@define_command
def _mask():
    """Invoke command line of mask mode."""
    widgets.cmdline.start(mode.Mask())

@define_command
def _menu():
    """Invoke command line of menu mode."""
    widgets.cmdline.start(mode.Menu())

@define_command
def _mkdir():
    """Invoke command line of mkdir mode."""
    widgets.cmdline.start(mode.Mkdir())

@define_command
def _move():
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
    """
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Move(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Move(), filer.file.name)

@define_command
def _newfile():
    """Invoke command line of new file mode."""
    widgets.cmdline.start(mode.Newfile())

@define_command
def _rename():
    """Invoke command line of rename mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Replace())
    else:
        cmdline.start(mode.Rename(), filer.file.name, -len(util.extname(filer.file.name))-1)

@define_command
def _replace():
    """Invoke command line of replace mode.
    The replace mode renames mark files with regexp.
    = Example:
    The extension of mark files is renamed from ".py" to ".txt"
    # Invoke replace mode by  +replace+  command.
    # The match pattern specify with regexp:
    $  $Replace pattern:$  \.py$
    # Specify the replacing string:
    $  $Replace regexp \.py\$ with:$  .txt
    """
    widgets.cmdline.start(mode.Replace())

@define_command
def _symlink():
    """Invoke command line of symlink mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Symlink(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Symlink(), os.path.join(filer.dir.path, filer.file.name))

@define_command
def _tar():
    """Invoke command line of tar mode."""
    tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
    if tarmode is None:
        return
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Tar(tarmode))
    else:
        cmdline.start(mode.Tar(tarmode), filer.file.name)

@define_command
def _tareach():
    """Invoke command line of tareach mode."""
    tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
    if tarmode is None:
        return
    widgets.cmdline.start(mode.Tar(tarmode, each=True))

@define_command
def _trashbox():
    """Invoke command line of trashbox mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    trashbox = os.path.expanduser(mode.TrashBox.path)
    if not os.path.exists(trashbox):
        if "Yes" == message.confirm("Trashbox doesn't exist. Make trashbox? ({0}):".format(trashbox), ["No", "Yes"]):
            try:
                os.makedirs(trashbox)
            except Exception as e:
                return message.exception(e)
        else:
            return
    if filer.dir.ismark():
        files = filer.dir.get_mark_files()
        ret = message.confirm("Move mark files to trashbox? ", ["No", "Yes"], files)
        if ret == "Yes":
            filectrl.move(files, trashbox)
    else:
        cmdline.start(mode.TrashBox(), filer.file.name)

@define_command
def _untar():
    """Invoke command line of untar mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.UnTar(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnTar(), filer.file.name)

@define_command
def _utime():
    """Invoke command line of utime mode."""
    widgets.cmdline.start(mode.Utime(), widgets.filer.file.name)

@define_command
def _unzip():
    """Invoke command line of unzip mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.UnZip(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnZip(), filer.file.name)

@define_command
def _zip():
    """Invoke command line of zip mode."""
    filer = widgets.filer
    cmdline = widgets.cmdline
    if filer.dir.ismark():
        cmdline.start(mode.Zip())
    else:
        cmdline.start(mode.Zip(), filer.file.name)

@define_command
def _zipeach():
    """Invoke command line of zipeach mode."""
    widgets.cmdline.start(mode.Zip(each=True))
