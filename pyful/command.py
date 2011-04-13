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
from pyful import filectrl
from pyful import message
from pyful import mode
from pyful import process
from pyful import ui
from pyful import util
from pyful import widget

commands = {}

def defcmd(func):
    commands[func.__name__.strip("_")] = func
    return func

# ----------------------------------------------------------------------
# Utility commands:
@defcmd
def _reload_rcfile():
    """Reload Pyful.environs["RCFILE"]"""
    try:
        path = Pyful.environs["RCFILE"]
        with open(path, "r") as rc:
            exec(rc.read(), locals())
        message.puts("Reloaded: {0}".format(path))
    except Exception as e:
        message.exception(e)

@defcmd
def _refresh_window():
    """Refresh all window."""
    ui.refresh()

@defcmd
def _rehash_programs():
    """Rehash of programs from PATH."""
    widget.get("Cmdline").completion.loadprograms()

@defcmd
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

@defcmd
def _spawn_editor():
    """Spawn the editor registered in Pyful.environs["EDITOR"]"""
    try:
        process.spawn(Pyful.environs["EDITOR"] + " %f")
    except Exception as e:
        message.exception(e)

@defcmd
def _spawn_shell():
    """Spawn the shell registered in pyful.process.Process.shell"""
    shell = process.Process.shell[0]
    try:
        process.spawn(shell, shell)
    except Exception as e:
        message.exception(e)

@defcmd
def _spawn_terminal():
    """Spawn the terminal registered in pyful.process.Process.terminal_emulator"""
    try:
        process.spawn(process.Process.terminal_emulator[0]+" %&")
    except Exception as e:
        message.exception(e)

@defcmd
def _exit():
    """Termination of application."""
    if "Yes" == message.confirm("Exit?", ["Yes", "No"]):
        sys.exit(0)

@defcmd
def _shell():
    """Invoke command line of shell mode."""
    widget.get("Cmdline").start(mode.Shell())

@defcmd
def _eval():
    """Invoke command line of eval mode."""
    widget.get("Cmdline").start(mode.Eval())

@defcmd
def _mx():
    """Invoke command line of mx mode."""
    widget.get("Cmdline").start(mode.Mx())

@defcmd
def _help():
    """Invoke command line of help mode."""
    widget.get("Cmdline").start(mode.Help())

@defcmd
def _help_all():
    """Show all command's help."""
    widget.get("Help").show_all_command()

@defcmd
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
    widget.get("Cmdline").start(mode.ChangeLooks())

@defcmd
def _google_search():
    """Search word in google on the regulated web browser."""
    widget.get("Cmdline").start(mode.WebSearch("Google"))

@defcmd
def _open_listfile():
    """Invoke command line of open list file mode."""
    widget.get("Cmdline").start(mode.OpenListfile())

@defcmd
def _message_history():
    """Display message history."""
    message.viewhistroy()

@defcmd
def _kill_thread():
    """Kill of a job threads."""
    filectrl.kill_thread()

@defcmd
def _drivejump():
    """Display the menu of an external disk where mount was done."""
    def _wrap(path):
        return lambda: widget.get("Filer").dir.chdir(path)
    menu = widget.get("Menu")
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

@defcmd
def _fileviewer():
    """File view by tar, zipinfo, unrar, 7z and Pyful.environs["PAGER"]."""
    ext = util.extname(widget.get("Filer").file.name)
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

@defcmd
def _pack():
    """File pack by tar, zip and rar."""
    ret = message.confirm("Pack type:", ["zip", "tgz", "bz2", "tar", "rar"])
    if "zip" == ret:
        _zip()
    elif ret == "tgz" or ret == "bz2" or ret == "tar":
        filer = widget.get("Filer")
        cmdline = widget.get("Cmdline")
        if filer.dir.ismark():
            cmdline.start(mode.Tar(ret))
        else:
            cmdline.start(mode.Tar(ret), filer.file.name)
    elif ret == "rar":
        widget.get("Cmdline").start(mode.Shell(), "rar u %D2.rar %m", -8)

@defcmd
def _unpack():
    """Unpack file of tar, zip and rar to neighbor directory."""
    ext = util.extname(widget.get("Filer").file.name)
    cmdline = widget.get("Cmdline")
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

@defcmd
def _unpack2():
    """Unpack file of tar, zip and rar to current directory."""
    ext = util.extname(widget.get("Filer").file.name)
    cmdline = widget.get("Cmdline")
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
@defcmd
def _enter_mark():
    """Behavior of mark files."""
    widget.get("Cmdline").start(mode.Shell(), " %m", 0)

@defcmd
def _enter_exec():
    """Behavior of executable file."""
    widget.get("Cmdline").start(mode.Shell(), " ./%f", 0)

@defcmd
def _enter_dir():
    """Behavior of directory."""
    widget.get("Filer").dir.enter_dir()

@defcmd
def _enter_link():
    """Behavior of symlink."""
    widget.get("Filer").dir.enter_link()

@defcmd
def _enter_listfile():
    """Behavior of list file.
    list file is a file to which the absolute path is written.
    """
    filer = widget.get("Filer")
    filer.dir.open_listfile(filer.file.name)

@defcmd
def _finder_start():
    """Start finder of focused directory."""
    widget.get("Filer").finder.start()

@defcmd
def _switch_workspace():
    """Switching workspaces."""
    filer = widget.get("Filer")
    titles = [w.title for w in filer.workspaces]
    pos = filer.cursor
    ret = message.confirm("Switch workspace:", options=titles, position=pos)
    for i, w in enumerate(filer.workspaces):
        if w.title == ret:
            filer.focus_workspace(i)
            break

@defcmd
def _create_workspace():
    """Create new workspace."""
    widget.get("Cmdline").start(mode.CreateWorkspace())

@defcmd
def _close_workspace():
    """Close current workspace."""
    widget.get("Filer").close_workspace()

@defcmd
def _change_workspace_title():
    """Change current workspace's title."""
    widget.get("Cmdline").start(mode.ChangeWorkspaceTitle())

@defcmd
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
    filer = widget.get("Filer")
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

@defcmd
def _switch_next_workspace():
    """Switching to next workspace."""
    widget.get("Filer").next_workspace()

@defcmd
def _switch_prev_workspace():
    """Switching to previous workspace."""
    widget.get("Filer").prev_workspace()

@defcmd
def _swap_workspace_inc():
    """Swap current workspace to next workspace."""
    widget.get("Filer").swap_workspace_inc()

@defcmd
def _swap_workspace_dec():
    """Swap current workspace to previous workspace."""
    widget.get("Filer").swap_workspace_dec()

@defcmd
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
    widget.get("Filer").workspace.tile()

@defcmd
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
    widget.get("Filer").workspace.tileleft()

@defcmd
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
    widget.get("Filer").workspace.tiletop()

@defcmd
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
    widget.get("Filer").workspace.tilebottom()

@defcmd
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
    widget.get("Filer").workspace.oneline()

@defcmd
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
    widget.get("Filer").workspace.onecolumn()

@defcmd
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
    widget.get("Filer").workspace.magnifier()

@defcmd
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
    widget.get("Filer").workspace.fullscreen()

@defcmd
def _chdir_parent():
    """Change current directory to parent directory."""
    widget.get("Filer").dir.chdir(os.pardir)

@defcmd
def _chdir_root():
    """Change current directory to root directory."""
    widget.get("Filer").dir.chdir("/")

@defcmd
def _chdir_home():
    """Change current directory to home directory."""
    widget.get("Filer").dir.chdir(os.getenv("HOME"))

@defcmd
def _chdir_neighbor():
    """Change current directory to neighbor directory."""
    filer = widget.get("Filer")
    filer.dir.chdir(filer.workspace.nextdir.path)

@defcmd
def _chdir_backward():
    """Change current directory to backward of directory history."""
    widget.get("Filer").dir.history.backward()

@defcmd
def _chdir_forward():
    """Change current directory to forward of directory history."""
    widget.get("Filer").dir.history.forward()

@defcmd
def _sort_name():
    """Sort name by ascending order."""
    widget.get("Filer").dir.sort_name()

@defcmd
def _sort_name_rev():
    """Sort name by descending order."""
    widget.get("Filer").dir.sort_name_rev()

@defcmd
def _sort_ext():
    """Sort file extension by ascending order."""
    widget.get("Filer").dir.sort_ext()

@defcmd
def _sort_ext_rev():
    """Sort file extension by descending order."""
    widget.get("Filer").dir.sort_ext_rev()

@defcmd
def _sort_size():
    """Sort file size by ascending order."""
    widget.get("Filer").dir.sort_size()

@defcmd
def _sort_size_rev():
    """Sort file size by descending order."""
    widget.get("Filer").dir.sort_size_rev()

@defcmd
def _sort_time():
    """Sort time by ascending order."""
    widget.get("Filer").dir.sort_time()

@defcmd
def _sort_time_rev():
    """Sort time by descending order."""
    widget.get("Filer").dir.sort_time_rev()

@defcmd
def _sort_nlink():
    """Sort link by ascending order."""
    widget.get("Filer").dir.sort_nlink()

@defcmd
def _sort_nlink_rev():
    """Sort link by descending order."""
    widget.get("Filer").dir.sort_nlink_rev()

@defcmd
def _sort_permission():
    """Sort permission by ascending order."""
    widget.get("Filer").dir.sort_permission()

@defcmd
def _sort_permission_rev():
    """Sort permission by ascending order."""
    widget.get("Filer").dir.sort_permission_rev()

@defcmd
def _toggle_view_ext():
    """Toggle the file extension display."""
    widget.get("Filer").toggle_view_ext()

@defcmd
def _toggle_view_permission():
    """Toggle the file permission display."""
    widget.get("Filer").toggle_view_permission()

@defcmd
def _toggle_view_nlink():
    """Toggle the nuber of link display."""
    widget.get("Filer").toggle_view_nlink()

@defcmd
def _toggle_view_user():
    """Toggle the user name of file display."""
    widget.get("Filer").toggle_view_user()

@defcmd
def _toggle_view_group():
    """Toggle the group name of file display."""
    widget.get("Filer").toggle_view_group()

@defcmd
def _toggle_view_size():
    """Toggle the file size display."""
    widget.get("Filer").toggle_view_size()

@defcmd
def _toggle_view_mtime():
    """Toggle the change time of file display."""
    widget.get("Filer").toggle_view_mtime()

@defcmd
def _create_dir():
    """Create directory in current workspace."""
    widget.get("Filer").workspace.create_dir()

@defcmd
def _close_dir():
    """Close focus directory in current workspace."""
    widget.get("Filer").workspace.close_dir()

@defcmd
def _all_reload():
    """Reload files of current workspace directorise."""
    widget.get("Filer").workspace.all_reload()

@defcmd
def _swap_dir_inc():
    """Swap current directory to next directory."""
    widget.get("Filer").workspace.swap_dir_inc()

@defcmd
def _swap_dir_dec():
    """Swap current directory to previous directory."""
    widget.get("Filer").workspace.swap_dir_dec()

@defcmd
def _focus_next_dir():
    """Focus of cursor to next directory."""
    widget.get("Filer").workspace.mvcursor(+1)

@defcmd
def _focus_prev_dir():
    """Focus of curosr to previous directory."""
    widget.get("Filer").workspace.mvcursor(-1)

@defcmd
def _filer_cursor_down():
    """Cursor down in focused directory."""
    widget.get("Filer").dir.mvcursor(+1)

@defcmd
def _filer_cursor_up():
    """Cursor up in focused directory."""
    widget.get("Filer").dir.mvcursor(-1)

@defcmd
def _filer_scroll_down():
    """Scroll down in focused directory."""
    widget.get("Filer").dir.mvscroll(+1)

@defcmd
def _filer_scroll_up():
    """Scroll up in focused directory."""
    widget.get("Filer").dir.mvscroll(-1)

@defcmd
def _filer_pagedown():
    """Page down in focused directory."""
    widget.get("Filer").dir.pagedown()

@defcmd
def _filer_pageup():
    """Page up in focused directory."""
    widget.get("Filer").dir.pageup()

@defcmd
def _filer_settop():
    """Set cursor to page top in focused directory."""
    widget.get("Filer").dir.settop()

@defcmd
def _filer_setbottom():
    """Set cursor to page bottom in focused directory."""
    widget.get("Filer").dir.setbottom()

@defcmd
def _filer_reset():
    """Reset the glob, mask and mark of focused directory."""
    widget.get("Filer").dir.reset()

# ----------------------------------------------------------------------
# Mark commands:
@defcmd
def _mark_all():
    """Mark all objects in current directory."""
    widget.get("Filer").dir.mark_all("all")

@defcmd
def _mark_file():
    """Mark all files in current directory."""
    widget.get("Filer").dir.mark_all("file")

@defcmd
def _mark_dir():
    """Mark all directories in current directory."""
    widget.get("Filer").dir.mark_all("directory")

@defcmd
def _mark_symlink():
    """Mark all symlinks in current directory."""
    widget.get("Filer").dir.mark_all("symlink")

@defcmd
def _mark_exec():
    """Mark all executable files in current directory."""
    widget.get("Filer").dir.mark_all("executable")

@defcmd
def _mark_socket():
    """Mark all sockets in current directory."""
    widget.get("Filer").dir.mark_all("socket")

@defcmd
def _mark_fifo():
    """Mark all fifo in current directory."""
    widget.get("Filer").dir.mark_all("fifo")

@defcmd
def _mark_chr():
    """Mark all chr files in current directory."""
    widget.get("Filer").dir.mark_all("chr")

@defcmd
def _mark_block():
    """Mark all block files in current directory."""
    widget.get("Filer").dir.mark_all("block")

@defcmd
def _mark_all_bcursor():
    """Mark all objects from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("all")

@defcmd
def _mark_file_bcursor():
    """Mark all files from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("file")

@defcmd
def _mark_dir_bcursor():
    """Mark all directries from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("directory")

@defcmd
def _mark_symlink_bcursor():
    """Mark all symlinks from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("symlink")

@defcmd
def _mark_exec_bcursor():
    """Mark all executable files from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("executable")

@defcmd
def _mark_socket_bcursor():
    """Mark all sockets from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("socket")

@defcmd
def _mark_fifo_bcursor():
    """Mark all fifo from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("fifo")

@defcmd
def _mark_chr_bcursor():
    """Mark all chr files from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("chr")

@defcmd
def _mark_block_bcursor():
    """Mark all block files from cursor in current directory."""
    widget.get("Filer").dir.mark_below_cursor("block")

@defcmd
def _mark_toggle():
    """Toggle mark of file under the cursor."""
    widget.get("Filer").dir.mark_toggle()

@defcmd
def _mark_toggle_all():
    """Toggle mark of all files in current directory."""
    widget.get("Filer").dir.mark_toggle_all()

@defcmd
def _mark_clear():
    """Clear mark of all files in current directory."""
    widget.get("Filer").dir.mark_clear()

# ----------------------------------------------------------------------
# Mask commands:
@defcmd
def _mask_clear():
    """Claer of filter."""
    widget.get("Filer").dir.mask(None)

# ----------------------------------------------------------------------
# File control  commands:
@defcmd
def _chdir():
    """Invoke command line of chdir mode."""
    widget.get("Cmdline").start(mode.Chdir(), widget.get("Filer").dir.path)

@defcmd
def _chmod():
    """Invoke command line of chmod mode."""
    widget.get("Cmdline").start(mode.Chmod())

@defcmd
def _chown():
    """Invoke command line of chown mode."""
    widget.get("Cmdline").start(mode.Chown())

@defcmd
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
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Copy(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Copy(), filer.file.name)

@defcmd
def _delete():
    """Invoke command line of delete mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        files = filer.dir.get_mark_files()
        ret = message.confirm("Delete mark files? ", ["No", "Yes"], files)
        if ret == "No" or ret is None:
            return
        filectrl.delete(files)
    else:
        cmdline.start(mode.Delete(), filer.file.name)

@defcmd
def _glob():
    """Invoke command line of glob mode."""
    widget.get("Cmdline").start(mode.Glob())

@defcmd
def _globdir():
    """Invoke command line of globdir mode."""
    widget.get("Cmdline").start(mode.GlobDir())

@defcmd
def _link():
    """Invoke command line of link mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Link(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Link(), filer.file.name)

@defcmd
def _mark():
    """Invoke command line of mark mode."""
    widget.get("Cmdline").start(mode.Mark())

@defcmd
def _mask():
    """Invoke command line of mask mode."""
    widget.get("Cmdline").start(mode.Mask())

@defcmd
def _menu():
    """Invoke command line of menu mode."""
    widget.get("Cmdline").start(mode.Menu())

@defcmd
def _mkdir():
    """Invoke command line of mkdir mode."""
    widget.get("Cmdline").start(mode.Mkdir())

@defcmd
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
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Move(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Move(), filer.file.name)

@defcmd
def _newfile():
    """Invoke command line of new file mode."""
    widget.get("Cmdline").start(mode.Newfile())

@defcmd
def _rename():
    """Invoke command line of rename mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Replace())
    else:
        cmdline.start(mode.Rename(), filer.file.name, -len(util.extname(filer.file.name))-1)

@defcmd
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
    widget.get("Cmdline").start(mode.Replace())

@defcmd
def _symlink():
    """Invoke command line of symlink mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Symlink(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.Symlink(), os.path.join(filer.dir.path, filer.file.name))

@defcmd
def _tar():
    """Invoke command line of tar mode."""
    tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
    if tarmode is None:
        return
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Tar(tarmode))
    else:
        cmdline.start(mode.Tar(tarmode), filer.file.name)

@defcmd
def _tareach():
    """Invoke command line of tareach mode."""
    tarmode = message.confirm("Tar mode:", ["gzip", "bzip2", "tar"])
    if tarmode is None:
        return
    widget.get("Cmdline").start(mode.Tar(tarmode, each=True))

@defcmd
def _trashbox():
    """Invoke command line of trashbox mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
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

@defcmd
def _untar():
    """Invoke command line of untar mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.UnTar(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnTar(), filer.file.name)

@defcmd
def _utime():
    """Invoke command line of utime mode."""
    widget.get("Cmdline").start(mode.Utime(), widget.get("Filer").file.name)

@defcmd
def _unzip():
    """Invoke command line of unzip mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.UnZip(), filer.workspace.nextdir.path)
    else:
        cmdline.start(mode.UnZip(), filer.file.name)

@defcmd
def _zip():
    """Invoke command line of zip mode."""
    filer = widget.get("Filer")
    cmdline = widget.get("Cmdline")
    if filer.dir.ismark():
        cmdline.start(mode.Zip())
    else:
        cmdline.start(mode.Zip(), filer.file.name)

@defcmd
def _zipeach():
    """Invoke command line of zipeach mode."""
    widget.get("Cmdline").start(mode.Zip(each=True))
