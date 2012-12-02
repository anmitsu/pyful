# -*-coding:utf-8-*-

# ======================================================================
# This file is pyful configuration file for setting editor, pager,
# keybinds, menus, etc.  This file must lacate as `~/.pyful/rc.py'.
# ======================================================================

import os
import sys

import pyful
from pyful import widgets
from pyful import command
from pyful import process

# ======================================================================
# Configure parameters
# ======================================================================

# Set environments of pyful.
pyful.Pyful.environs["EDITOR"] = "vim"
pyful.Pyful.environs["PAGER"] = "lv"

# Set proc attributes.
pyful.process.Process.shell = ("/bin/bash", "-c")
pyful.process.Process.terminal_emulator = ("x-terminal-emulator", "-e")

# Set screen command and arguments.
#     {TITLE} is replaced to window title in screen.
#     {COMMAND} is replaced to a command in screen.
if os.getenv("TMUX"):
    # For tmux:
    pyful.process.Process.screen_command = ("tmux", "neww", "-n", "{TITLE}", "{COMMAND}")
else:
    # For GNU Screen:
    pyful.process.Process.screen_command = ("screen", "-t", "{TITLE}", "bash", "-c", "{COMMAND}")

# Set the mode of mkdir and newfile in octal number.
pyful.mode.Mkdir.dirmode = 0o755
pyful.mode.Newfile.filemode = 0o644
pyful.mode.TrashBox.path = "~/.pyful/trashbox"
pyful.mode.Replace.form = "vim" # or "emacs"

# Set the prompt of shell mode.
pyful.mode.Shell.prompt = " $ "

# Set message history.
pyful.message.Message.history = 100

# Set height of message box.
pyful.message.MessageBox.height = 4

# Set the default path of the directory creating.
pyful.filer.Workspace.default_path = "~/"

# Set the workspace layout.
#     "Tile"
#     "TileLeft"
#     "TileTop"
#     "TileBottom"
#     "Oneline"
#     "Onecolumn"
#     "Magnifier"
#     "Fullscreen"
pyful.filer.Workspace.layout = "Tile"

# Set default kind of sorting in directory.
#     "Name[^]" -> Name sort of ascending order;
#     "Name[$]" -> Name sort of descending order;
#     "Size[^]" -> File size sort of ascending order;
#     "Size[$]" -> File size sort of descending order;
#     "Time[^]" -> Time sort of ascending order;
#     "Time[$]" -> Time sort of descending order;
#     "Permission[^]" -> Permission sort of ascending order;
#     "Permission[$]" -> Permission sort of descending order;
#     "Link[^]" -> Link sort of ascending order;
#     "Link[$]" -> Link sort of descending order;
#     "Ext[^]" -> File extension sort of ascending order;
#     "Ext[$]" -> File extension sort of descending order.
pyful.filer.Directory.sort_kind = "Name[^]"

# Is a directory sorted in upwards?
pyful.filer.Directory.sort_updir = False

# Set scroll type in directory.
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
pyful.filer.Directory.scroll_type = "HalfScroll"

# Set statusbar format in directory.
pyful.filer.Directory.statusbar_format = " [{MARK}/{FILE}] {MARKSIZE}bytes {SCROLL}({CURSOR}) {SORT} "

# Distinguish upper case and lower case at a finder?
pyful.filer.Finder.smartcase = True

# Set PyMigemo and migemo dictionary.
# It is necessary to install PyMigemo to use migemo.
try:
    import migemo
    if not pyful.filer.Finder.migemo:
        pyful.filer.Finder.migemo = migemo.Migemo("/usr/share/cmigemo/utf-8/migemo-dict")
except (ImportError, ValueError):
    pyful.filer.Finder.migemo = None

# Set the time format of file.
# It conforms to the strftime format from time module.
pyful.filer.FileStat.time_format = "%y-%m-%d %H:%M"
# pyful.filer.FileStat.time_format = "%c(%a)"
# pyful.filer.FileStat.time_format = "%c"

# Set the flag of file modified within 24 hours.
pyful.filer.FileStat.time_24_flag = "!"
# Set the flag of file modified within a week.
pyful.filer.FileStat.time_week_flag = "#"
# Set the flag of file modified more in old time.
pyful.filer.FileStat.time_yore_flag = " "

# Display the file extension?
pyful.filer.FileStat.draw_ext = True
# Display the file permission?
pyful.filer.FileStat.draw_permission = True
# Display the number of link?
pyful.filer.FileStat.draw_nlink = False
# Display the user name of file?
pyful.filer.FileStat.draw_user = False
# Display the group name of file?
pyful.filer.FileStat.draw_group = False
# Display the file size?
pyful.filer.FileStat.draw_size = True
# Display the change time of file?
pyful.filer.FileStat.draw_mtime = True

# Set my look.
#     "default"
#     "midnight"
#     "dark"
#     "light"
pyful.look.Look.mylook = "default"

# Set borders.
# Smooth borders:
pyful.widget.base.StandardScreen.borders = []
pyful.widget.listbox.ListBox.borders = []
# Classical borders:
# pyful.widget.base.StandardScreen.borders = ["|", "|", "-", "-", "+", "+", "+", "+"]
# pyful.widget.listbox.ListBox.borders = ["|", "|", "-", "-", "+", "+", "+", "+"]

# Set zoom attribute of listbox.
pyful.widget.listbox.ListBox.zoom = 0

# Set scroll type in listbox.
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
pyful.widget.listbox.ListBox.scroll_type = "HalfScroll"

# Enable mouse support?
pyful.widget.ui.MouseHandler.enable(False)

# Set cmdline attributes.
pyful.cmdline.History.maxsave = 10000
pyful.cmdline.Clipboard.maxsave = 100

# Registration of program initialization.
# Pyful.atinit() wraps the initialization functions.
@pyful.Pyful.atinit
def myatinit():
    widgets.filer.loadfile("~/.pyfulinfo.json")
    widgets.cmdline.clipboard.loadfile("~/.pyful/clipboard")
    widgets.cmdline.history.loadfile("~/.pyful/history/shell", "Shell")
    widgets.cmdline.history.loadfile("~/.pyful/history/eval", "Eval")
    widgets.cmdline.history.loadfile("~/.pyful/history/mx", "Mx")
    widgets.cmdline.history.loadfile("~/.pyful/history/replace", "Replace")

# Registration of program termination.
# Pyful.atexit() wraps the termination functions.
@pyful.Pyful.atexit
def myatexit():
    widgets.filer.savefile("~/.pyfulinfo.json")
    widgets.cmdline.clipboard.savefile("~/.pyful/clipboard")
    widgets.cmdline.history.savefile("~/.pyful/history/shell", "Shell")
    widgets.cmdline.history.savefile("~/.pyful/history/eval", "Eval")
    widgets.cmdline.history.savefile("~/.pyful/history/mx", "Mx")
    widgets.cmdline.history.savefile("~/.pyful/history/replace", "Replace")

# ======================================================================
# Define keymaps for widgets of pyful.
#
# A key of the keymap dictionary is key or (key, ext).
# A value of the keymap dictionary is the callable function of no argument.
#     "C-a" -> Ctrl + a
#     "M-a" -> Meta + a
#     "M-C-a" -> Meta + Ctrl + a
#     "A" -> Shift + a
#     "RET" -> Enter or Ctrl + m
#     "ESC" -> Escape
#     "SPC" -> Space
#     "<name>" -> Constants in curses module: KEY_name
#
# The following extension names are special:
#     ".dir" represent the directory;
#     ".link" represent the symbolic link;
#     ".exec" represent the executable file;
#     ".mark" represent the mark file.
#
# Note:
#     "C-m" key is interpreted as "RET" in most terminals.
#     The key such as "C-A" are interpreted such as "C-a".
#     The key such as "C-<down>" are undefine.
# ======================================================================

pyful.widget.define_key(widgets.filer, {
        "M-f"           : lambda: command.run("switch_next_workspace"),
        "M-b"           : lambda: command.run("switch_prev_workspace"),
        "M-F"           : lambda: command.run("swap_workspace_inc"),
        "M-B"           : lambda: command.run("swap_workspace_dec"),
        "C-i"           : lambda: command.run("focus_next_dir"),
        "C-f"           : lambda: command.run("focus_next_dir"),
        "C-b"           : lambda: command.run("focus_prev_dir"),
        "<right>"       : lambda: command.run("focus_next_dir"),
        "<left>"        : lambda: command.run("focus_prev_dir"),
        "F"             : lambda: command.run("swap_dir_inc"),
        "B"             : lambda: command.run("swap_dir_dec"),
        "M-C-j"         : lambda: command.run("create_dir"),
        "M-C"           : lambda: command.run("close_dir"),
        "C-w"           : lambda: command.run("close_dir"),
        "C-l"           : lambda: command.run("all_reload"),
        "C-n"           : lambda: command.run("filer_cursor_down"),
        "<down>"        : lambda: command.run("filer_cursor_down"),
        "C-p"           : lambda: command.run("filer_cursor_up"),
        "<up>"          : lambda: command.run("filer_cursor_up"),
        "C-d"           : lambda: command.run("filer_cursor_more_down"),
        "C-u"           : lambda: command.run("filer_cursor_more_up"),
        "M-n"           : lambda: command.run("filer_scroll_down"),
        "M-p"           : lambda: command.run("filer_scroll_up"),
        "C-v"           : lambda: command.run("filer_pagedown"),
        "<npage>"       : lambda: command.run("filer_pagedown"),
        "M-v"           : lambda: command.run("filer_pageup"),
        "<ppage>"       : lambda: command.run("filer_pageup"),
        "C-a"           : lambda: command.run("filer_settop"),
        "M-<"           : lambda: command.run("filer_settop"),
        "C-e"           : lambda: command.run("filer_setbottom"),
        "M->"           : lambda: command.run("filer_setbottom"),
        "C-g"           : lambda: command.run("filer_reset"),
        "ESC"           : lambda: command.run("filer_reset"),
        "M-w"           : lambda: command.run("switch_workspace"),
        "M-h"           : lambda: command.run("chdir_backward"),
        "M-l"           : lambda: command.run("chdir_forward"),
        "C-h"           : lambda: command.run("chdir_parent"),
        "<backspace>"   : lambda: command.run("chdir_parent"),
        "~"             : lambda: command.run("chdir_home"),
        "\\"            : lambda: command.run("chdir_root"),
        "w"             : lambda: command.run("chdir_neighbor"),
        "f"             : lambda: command.run("finder_start"),
        "/"             : lambda: command.run("finder_start"),
        "v"             : lambda: command.run("fileviewer"),
        "P"             : lambda: command.run("pack"),
        "U"             : lambda: command.run("unpack2"),
        "u"             : lambda: command.run("unpack"),
        "J"             : lambda: command.run("drivejump"),
        "<end>"         : lambda: command.run("mark_toggle_all"),
        "SPC"           : lambda: command.run("mark_toggle"),
        "C-r"           : lambda: command.run("refresh_window"),
        "RET"           : lambda: command.run("open_at_system"),
        "C-j"           : lambda: command.run("open_at_system"),
        "e"             : lambda: command.run("spawn_editor"),
        ":"             : lambda: command.run("spawn_shell"),
        "h"             : lambda: command.run("shell"),
        "M-:"           : lambda: command.run("eval"),
        "M-x"           : lambda: command.run("mx"),
        "M-m"           : lambda: command.run("menu"),
        "K"             : lambda: command.run("kill_thread"),
        "?"             : lambda: command.run("help"),
        "M-?"           : lambda: command.run("help_all"),
        "c"             : lambda: command.run("copy"),
        "<dc>"          : lambda: command.run("delete"),
        "D"             : lambda: command.run("delete"),
        "k"             : lambda: command.run("mkdir"),
        "m"             : lambda: command.run("move"),
        "n"             : lambda: command.run("newfile"),
        "r"             : lambda: command.run("rename"),
        "R"             : lambda: command.run("replace"),
        "l"             : lambda: command.run("symlink"),
        "d"             : lambda: command.run("trashbox"),
        "t"             : lambda: command.run("utime"),
        "x"             : lambda: command.run("enter_exec"),
        "*"             : lambda: command.run("mark"),
        "+"             : lambda: command.run("mask"),
        "q"             : lambda: command.run("exit"),
        "Q"             : lambda: command.run("exit"),
        ("RET", ".dir" ): lambda: command.run("enter_dir"),
        ("RET", ".mark"): lambda: command.run("enter_mark"),
        ("RET", ".link"): lambda: command.run("enter_link"),
        ("RET", ".exec"): lambda: command.run("enter_exec"),
        ("RET", ".tar" ): lambda: command.run("untar"),
        ("RET", ".tgz" ): lambda: command.run("untar"),
        ("RET", ".gz"  ): lambda: command.run("untar"),
        ("RET", ".bz2" ): lambda: command.run("untar"),
        ("RET", ".zip" ): lambda: command.run("unzip"),
        ("RET", ".list"): lambda: command.run("enter_listfile"),
        })

pyful.widget.define_key(widgets.filer.finder, {
        "M-n"         : lambda: widgets.filer.finder.history_select(-1),
        "M-p"         : lambda: widgets.filer.finder.history_select(+1),
        "C-g"         : lambda: widgets.filer.finder.finish(),
        "ESC"         : lambda: widgets.filer.finder.finish(),
        "C-c"         : lambda: widgets.filer.finder.finish(),
        "C-h"         : lambda: widgets.filer.finder.delete_backward_char(),
        "<backspace>" : lambda: widgets.filer.finder.delete_backward_char(),
        })

pyful.widget.define_key(widgets.cmdline, {
        "C-f"         : lambda: widgets.cmdline.forward_char(),
        "<right>"     : lambda: widgets.cmdline.forward_char(),
        "C-b"         : lambda: widgets.cmdline.backward_char(),
        "<left>"      : lambda: widgets.cmdline.backward_char(),
        "M-f"         : lambda: widgets.cmdline.forward_word(),
        "M-b"         : lambda: widgets.cmdline.backward_word(),
        "C-d"         : lambda: widgets.cmdline.delete_char(),
        "<dc>"        : lambda: widgets.cmdline.delete_char(),
        "C-h"         : lambda: widgets.cmdline.delete_backward_char(),
        "<backspace>" : lambda: widgets.cmdline.delete_backward_char(),
        "M-d"         : lambda: widgets.cmdline.delete_forward_word(),
        "M-h"         : lambda: widgets.cmdline.delete_backward_word(),
        "C-w"         : lambda: widgets.cmdline.delete_backward_word(),
        "C-k"         : lambda: widgets.cmdline.kill_line(),
        "C-u"         : lambda: widgets.cmdline.kill_line_all(),
        "C-a"         : lambda: widgets.cmdline.settop(),
        "C-e"         : lambda: widgets.cmdline.setbottom(),
        "C-g"         : lambda: widgets.cmdline.escape(),
        "C-c"         : lambda: widgets.cmdline.escape(),
        "ESC"         : lambda: widgets.cmdline.escape(),
        "RET"         : lambda: widgets.cmdline.execute(),
        "M-i"         : lambda: widgets.cmdline.select_action(),
        "M-m"         : lambda: widgets.cmdline.expandmacro(),
        "C-y"         : lambda: widgets.cmdline.clipboard.paste(),
        "M-y"         : lambda: widgets.cmdline.clipboard.start(),
        "C-i"         : lambda: widgets.cmdline.completion.start(),
        "M-j"         : lambda: widgets.cmdline.output.communicate(),
        "C-n"         : lambda: widgets.cmdline.history.mvcursor(+1),
        "<down>"      : lambda: widgets.cmdline.history.mvcursor(+1),
        "C-p"         : lambda: widgets.cmdline.history.mvcursor(-1),
        "<up>"        : lambda: widgets.cmdline.history.mvcursor(-1),
        "M-n"         : lambda: widgets.cmdline.history.mvscroll(+1),
        "M-p"         : lambda: widgets.cmdline.history.mvscroll(-1),
        "C-v"         : lambda: widgets.cmdline.history.pagedown(),
        "M-v"         : lambda: widgets.cmdline.history.pageup(),
        "M-<"         : lambda: widgets.cmdline.history.settop(),
        "M->"         : lambda: widgets.cmdline.history.setbottom(),
        "C-x"         : lambda: widgets.cmdline.history.delete(),
        "M-+"         : lambda: widgets.cmdline.history.zoombox(+5),
        "M--"         : lambda: widgets.cmdline.history.zoombox(-5),
        "M-="         : lambda: widgets.cmdline.history.zoombox(0),
        })

pyful.widget.define_key(widgets.cmdline.clipboard, {
        "C-n"         : lambda: widgets.cmdline.clipboard.mvcursor(1),
        "<down>"      : lambda: widgets.cmdline.clipboard.mvcursor(1),
        "C-v"         : lambda: widgets.cmdline.clipboard.pagedown(),
        "C-d"         : lambda: widgets.cmdline.clipboard.pagedown(),
        "C-p"         : lambda: widgets.cmdline.clipboard.mvcursor(-1),
        "<up>"        : lambda: widgets.cmdline.clipboard.mvcursor(-1),
        "M-v"         : lambda: widgets.cmdline.clipboard.pageup(),
        "C-u"         : lambda: widgets.cmdline.clipboard.pageup(),
        "M-n"         : lambda: widgets.cmdline.clipboard.mvscroll(+1),
        "M-p"         : lambda: widgets.cmdline.clipboard.mvscroll(-1),
        "C-x"         : lambda: widgets.cmdline.clipboard.delete(),
        "C-g"         : lambda: widgets.cmdline.clipboard.finish(),
        "C-c"         : lambda: widgets.cmdline.clipboard.finish(),
        "ESC"         : lambda: widgets.cmdline.clipboard.finish(),
        "RET"         : lambda: widgets.cmdline.clipboard.insert(),
        "M-+"         : lambda: widgets.cmdline.clipboard.zoombox(+5),
        "M--"         : lambda: widgets.cmdline.clipboard.zoombox(-5),
        "M-="         : lambda: widgets.cmdline.clipboard.zoombox(0),
        "C-f"         : lambda: widgets.cmdline.clipboard.textbox.forward_char(),
        "<right>"     : lambda: widgets.cmdline.clipboard.textbox.forward_char(),
        "C-b"         : lambda: widgets.cmdline.clipboard.textbox.backward_char(),
        "<left>"      : lambda: widgets.cmdline.clipboard.textbox.backward_char(),
        "M-f"         : lambda: widgets.cmdline.clipboard.textbox.forward_word(),
        "M-b"         : lambda: widgets.cmdline.clipboard.textbox.backward_word(),
        "C-d"         : lambda: widgets.cmdline.clipboard.textbox.delete_char(),
        "<dc>"        : lambda: widgets.cmdline.clipboard.textbox.delete_char(),
        "C-h"         : lambda: widgets.cmdline.clipboard.textbox.delete_backward_char(),
        "<backspace>" : lambda: widgets.cmdline.clipboard.textbox.delete_backward_char(),
        "M-d"         : lambda: widgets.cmdline.clipboard.textbox.delete_forward_word(),
        "M-h"         : lambda: widgets.cmdline.clipboard.textbox.delete_backward_word(),
        "C-w"         : lambda: widgets.cmdline.clipboard.textbox.delete_backward_word(),
        "C-k"         : lambda: widgets.cmdline.clipboard.textbox.kill_line(),
        "C-u"         : lambda: widgets.cmdline.clipboard.textbox.kill_line_all(),
        "C-a"         : lambda: widgets.cmdline.clipboard.textbox.settop(),
        "C-e"         : lambda: widgets.cmdline.clipboard.textbox.setbottom(),
        })

pyful.widget.define_key(widgets.cmdline.completion, {
        "C-n"     : lambda: widgets.cmdline.completion.cursordown(),
        "<down>"  : lambda: widgets.cmdline.completion.cursordown(),
        "C-p"     : lambda: widgets.cmdline.completion.cursorup(),
        "<up>"    : lambda: widgets.cmdline.completion.cursorup(),
        "C-i"     : lambda: widgets.cmdline.completion.mvcursor(+1),
        "C-f"     : lambda: widgets.cmdline.completion.mvcursor(+1),
        "<right>" : lambda: widgets.cmdline.completion.mvcursor(+1),
        "C-b"     : lambda: widgets.cmdline.completion.mvcursor(-1),
        "<left>"  : lambda: widgets.cmdline.completion.mvcursor(-1),
        "M-n"     : lambda: widgets.cmdline.completion.mvscroll(+1),
        "M-p"     : lambda: widgets.cmdline.completion.mvscroll(-1),
        "C-v"     : lambda: widgets.cmdline.completion.pagedown(),
        "M-v"     : lambda: widgets.cmdline.completion.pageup(),
        "C-g"     : lambda: widgets.cmdline.completion.finish(),
        "C-c"     : lambda: widgets.cmdline.completion.finish(),
        "ESC"     : lambda: widgets.cmdline.completion.finish(),
        "RET"     : lambda: widgets.cmdline.completion.insert(),
        "M-+"     : lambda: widgets.cmdline.completion.zoombox(+5),
        "M--"     : lambda: widgets.cmdline.completion.zoombox(-5),
        "M-="     : lambda: widgets.cmdline.completion.zoombox(0),
        })

pyful.widget.define_key(widgets.cmdline.output, {
        "C-n"    : lambda: widgets.cmdline.output.mvcursor(1),
        "<down>" : lambda: widgets.cmdline.output.mvcursor(1),
        "C-v"    : lambda: widgets.cmdline.output.pagedown(),
        "C-d"    : lambda: widgets.cmdline.output.pagedown(),
        "C-p"    : lambda: widgets.cmdline.output.mvcursor(-1),
        "<up>"   : lambda: widgets.cmdline.output.mvcursor(-1),
        "M-v"    : lambda: widgets.cmdline.output.pageup(),
        "C-u"    : lambda: widgets.cmdline.output.pageup(),
        "M-n"    : lambda: widgets.cmdline.output.mvscroll(+1),
        "M-p"    : lambda: widgets.cmdline.output.mvscroll(-1),
        "C-g"    : lambda: widgets.cmdline.output.finish(),
        "C-c"    : lambda: widgets.cmdline.output.finish(),
        "ESC"    : lambda: widgets.cmdline.output.finish(),
        "RET"    : lambda: widgets.cmdline.output.edit(),
        "M-+"    : lambda: widgets.cmdline.output.zoombox(+5),
        "M--"    : lambda: widgets.cmdline.output.zoombox(-5),
        "M-="    : lambda: widgets.cmdline.output.zoombox(0),
        })

pyful.widget.define_key(widgets.help, {
        "j"      : lambda: widgets.help.mvcursor(1),
        "C-n"    : lambda: widgets.help.mvcursor(1),
        "<down>" : lambda: widgets.help.mvcursor(1),
        "k"      : lambda: widgets.help.mvcursor(-1),
        "C-p"    : lambda: widgets.help.mvcursor(-1),
        "<up>"   : lambda: widgets.help.mvcursor(-1),
        "C-v"    : lambda: widgets.help.pagedown(),
        "C-d"    : lambda: widgets.help.pagedown(),
        "M-v"    : lambda: widgets.help.pageup(),
        "C-u"    : lambda: widgets.help.pageup(),
        "M-n"    : lambda: widgets.help.mvscroll(+1),
        "M-p"    : lambda: widgets.help.mvscroll(-1),
        "C-g"    : lambda: widgets.help.hide(),
        "C-c"    : lambda: widgets.help.hide(),
        "ESC"    : lambda: widgets.help.hide(),
        "M-+"    : lambda: widgets.help.zoombox(+5),
        "M--"    : lambda: widgets.help.zoombox(-5),
        "M-="    : lambda: widgets.help.zoombox(0),
        })

pyful.widget.define_key(widgets.menu, {
        "C-n"    : lambda: widgets.menu.mvcursor(+1),
        "<down>" : lambda: widgets.menu.mvcursor(+1),
        "C-p"    : lambda: widgets.menu.mvcursor(-1),
        "<up>"   : lambda: widgets.menu.mvcursor(-1),
        "C-d"    : lambda: widgets.menu.mvcursor(+5),
        "C-u"    : lambda: widgets.menu.mvcursor(-5),
        "C-v"    : lambda: widgets.menu.pagedown(),
        "M-v"    : lambda: widgets.menu.pageup(),
        "M-n"    : lambda: widgets.menu.mvscroll(+1),
        "M-p"    : lambda: widgets.menu.mvscroll(-1),
        "C-a"    : lambda: widgets.menu.settop(),
        "M-<"    : lambda: widgets.menu.settop(),
        "C-e"    : lambda: widgets.menu.setbottom(),
        "M->"    : lambda: widgets.menu.setbottom(),
        "C-g"    : lambda: widgets.menu.hide(),
        "C-c"    : lambda: widgets.menu.hide(),
        "ESC"    : lambda: widgets.menu.hide(),
        "RET"    : lambda: widgets.menu.run(),
        })

pyful.widget.define_key(widgets.message.confirmbox, {
        "C-f"     : lambda: widgets.message.confirmbox.mvcursor(1),
        "<right>" : lambda: widgets.message.confirmbox.mvcursor(1),
        "C-b"     : lambda: widgets.message.confirmbox.mvcursor(-1),
        "<left>"  : lambda: widgets.message.confirmbox.mvcursor(-1),
        "C-a"     : lambda: widgets.message.confirmbox.settop(),
        "C-e"     : lambda: widgets.message.confirmbox.setbottom(),
        "C-c"     : lambda: widgets.message.confirmbox.hide(),
        "C-g"     : lambda: widgets.message.confirmbox.hide(),
        "ESC"     : lambda: widgets.message.confirmbox.hide(),
        "RET"     : lambda: widgets.message.confirmbox.get_result(),
        "C-n"     : lambda: widgets.message.confirmbox.listbox.mvcursor(1),
        "<down>"  : lambda: widgets.message.confirmbox.listbox.mvcursor(1),
        "C-p"     : lambda: widgets.message.confirmbox.listbox.mvcursor(-1),
        "<up>"    : lambda: widgets.message.confirmbox.listbox.mvcursor(-1),
        "M-n"     : lambda: widgets.message.confirmbox.listbox.mvscroll(1),
        "M-p"     : lambda: widgets.message.confirmbox.listbox.mvscroll(-1),
        "C-v"     : lambda: widgets.message.confirmbox.listbox.pagedown(),
        "M-v"     : lambda: widgets.message.confirmbox.listbox.pageup(),
        "M-+"     : lambda: widgets.message.confirmbox.listbox.zoombox(+5),
        "M--"     : lambda: widgets.message.confirmbox.listbox.zoombox(-5),
        "M-="     : lambda: widgets.message.confirmbox.listbox.zoombox(0),
        })

pyful.widget.define_key(widgets.action, {
        "C-n"    : lambda: widgets.action.mvcursor(1),
        "<down>" : lambda: widgets.action.mvcursor(1),
        "C-v"    : lambda: widgets.action.pagedown(),
        "C-d"    : lambda: widgets.action.pagedown(),
        "C-p"    : lambda: widgets.action.mvcursor(-1),
        "<up>"   : lambda: widgets.action.mvcursor(-1),
        "M-n"    : lambda: widgets.action.mvscroll(1),
        "M-p"    : lambda: widgets.action.mvscroll(-1),
        "M-v"    : lambda: widgets.action.pageup(),
        "C-u"    : lambda: widgets.action.pageup(),
        "C-g"    : lambda: widgets.action.hide(),
        "C-c"    : lambda: widgets.action.hide(),
        "ESC"    : lambda: widgets.action.hide(),
        "M-+"    : lambda: widgets.action.zoombox(+5),
        "M--"    : lambda: widgets.action.zoombox(-5),
        "M-="    : lambda: widgets.action.zoombox(0),
        "RET"    : lambda: widgets.action.select_action(),
        })

# ======================================================================
# Define the menu.
#
# A key of the menu item dictionary is the menu title.
#
# A value of the menu item dictionary must be the sequence that
# consist of the sequence that meet the following requirement:
#     - The first element is the menu item title;
#     - The second element is the key symbol;
#     - The third element is the callable function of no argument.
# ======================================================================

pyful.menu.define_menu("Main", (
    ("File" , "f", lambda: widgets.menu.show("File")),
    ("Edit" , "e", lambda: widgets.menu.show("Edit")),
    ("View" , "v", lambda: widgets.menu.show("View")),
    ("Go"   , "g", lambda: widgets.menu.show("Go")),
    ("Tool" , "t", lambda: widgets.menu.show("Tool")),
    ("Help" , "h", lambda: widgets.menu.show("Help")),
    ))

pyful.menu.define_menu("File", (
    ("New file"        ,  "n", lambda: command.run("newfile")),
    ("New directory"   ,  "k", lambda: command.run("mkdir")),
    ("New workspace"   ,  "w", lambda: command.run("create_workspace")),
    ("New dirview"     ,  "d", lambda: command.run("create_dir")),
    ("Open"            ,  "o", lambda: command.run("open_at_system")),
    ("Close workspace" ,  "W", lambda: command.run("close_workspace")),
    ("Close dirview"   ,  "D", lambda: command.run("close_dir")),
    ("Exit"            ,  "q", lambda: command.run("exit")),
    ))

pyful.menu.define_menu("Edit", (
    ("Copy"           ,  "c"     , lambda: command.run("copy")),
    ("Move"           ,  "m"     , lambda: command.run("move")),
    ("Delete"         ,  "D"     , lambda: command.run("delete")),
    ("Trashbox"       ,  "d"     , lambda: command.run("trashbox")),
    ("Toggle mark"    ,  "SPC"   , lambda: command.run("mark_toggle")),
    ("All mark"       ,  "<end>" , lambda: command.run("mark_toggle_all")),
    ("Rename"         ,  "r"     , lambda: command.run("rename")),
    ("Replace"        ,  "R"     , lambda: command.run("replace")),
    ("Create symlink" ,  "l"     , lambda: command.run("symlink")),
    ("Create link"    ,  "L"     , lambda: command.run("link")),
    ("Change mtime"   ,  "t"     , lambda: command.run("utime")),
    ("Chmod"          ,  "M"     , lambda: command.run("chmod")),
    ("Chown"          ,  "O"     , lambda: command.run("chown")),
    ("Archive"        ,  "a"     , lambda: widgets.menu.show("archive")),
    ))

pyful.menu.define_menu("View", (
    ("Reload"         , "C-l" , lambda: command.run("all_reload")),
    ("Refresh window" , "C-r" , lambda: command.run("refresh_window")),
    ("Info to view"   , "V"   , lambda: widgets.menu.show("fileinfo")),
    ("Sort"           , "s"   , lambda: widgets.menu.show("sort")),
    ("Layout"         , "L"   , lambda: widgets.menu.show("layout")),
    ("Filter mask"    , "m"   , lambda: command.run("mask")),
    ))

pyful.menu.define_menu("Go", (
    ("To parent"        , "C-h" , lambda: command.run("chdir_parent")),
    ("To home"          , "~"   , lambda: command.run("chdir_home")),
    ("To root"          , "\\"  , lambda: command.run("chdir_root")),
    ("To neighbor"      , "w"   , lambda: command.run("chdir_neighbor")),
    ("Backward history" , "M-h" , lambda: command.run("chdir_backward")),
    ("Forward history"  , "M-l" , lambda: command.run("chdir_forward")),
    ("Finder start"     , "f"   , lambda: command.run("finder_start")),
    ("Bookmark"         , "b"   , lambda: widgets.menu.show("bookmark")),
    ))

pyful.menu.define_menu("Tool", (
    ("Shell"           ,  "h"   , lambda: command.run("shell")),
    ("Eval"            ,  "M-:" , lambda: command.run("eval")),
    ("Command"         ,  "M-x" , lambda: command.run("mx")),
    ("Glob search"     ,  "g"   , lambda: command.run("glob")),
    ("Glob recursive"  ,  "G"   , lambda: command.run("globdir")),
    ("Rehash programs" ,  "r"   , lambda: command.run("rehash_programs")),
    ("Reload rc.py"    ,  "R"   , lambda: command.run("reload_rcfile")),
    ("Editor"          ,  "E"   , lambda: widgets.menu.show("editor")),
    ("Web browser"     ,  "w"   , lambda: widgets.menu.show("webbrowser")),
    ("File manager"    ,  "f"   , lambda: widgets.menu.show("filemanager")),
    ))

pyful.menu.define_menu("Help", (
    ("Help"     ,  "h", lambda: command.run("help")),
    ("Help all" ,  "H", lambda: command.run("help_all")),
    ))

pyful.menu.define_menu("archive", (
    ("Zip"            , "z", lambda: command.run("zip")),
    ("Zip each files" , "Z", lambda: command.run("zipeach")),
    ("Tar"            , "t", lambda: command.run("zip")),
    ("Tar each files" , "T", lambda: command.run("zipeach")),
    ("Inflat zip"     , "i", lambda: command.run("unzip")),
    ("Extract tar"    , "e", lambda: command.run("untar")),
    ))

pyful.menu.define_menu("bookmark", (
    ("/etc" , "e", lambda: widgets.filer.dir.chdir("/etc")),
    ("/usr" , "u", lambda: widgets.filer.dir.chdir("/usr")),
    ))

pyful.menu.define_menu("fileinfo", (
    ("toggle extension" , "e", lambda: command.run("toggle_draw_ext")),
    ("toggle permission", "p", lambda: command.run("toggle_draw_permission")),
    ("toggle nlink"     , "l", lambda: command.run("toggle_draw_nlink")),
    ("toggle user"      , "u", lambda: command.run("toggle_draw_user")),
    ("toggle group"     , "g", lambda: command.run("toggle_draw_group")),
    ("toggle size"      , "s", lambda: command.run("toggle_draw_size")),
    ("toggle mtime"     , "t", lambda: command.run("toggle_draw_mtime")),
    ))

pyful.menu.define_menu("layout", (
    ("tile"        , "t", lambda: command.run("layout_tile")),
    ("tileLeft"    , "L", lambda: command.run("layout_tileleft")),
    ("tileTop"     , "T", lambda: command.run("layout_tiletop")),
    ("tileBottom"  , "B", lambda: command.run("layout_tilebottom")),
    ("oneline"     , "l", lambda: command.run("layout_oneline")),
    ("onecolumn"   , "c", lambda: command.run("layout_onecolumn")),
    ("magnifier"   , "m", lambda: command.run("layout_magnifier")),
    ("fullscreen"  , "f", lambda: command.run("layout_fullscreen")),
    ))

pyful.menu.define_menu("sort", (
    ("name"              , "n", lambda: command.run("sort_name")),
    ("name reverse"      , "N", lambda: command.run("sort_name_rev")),
    ("extension"         , "e", lambda: command.run("sort_ext")),
    ("extension reverse" , "E", lambda: command.run("sort_ext_rev")),
    ("size"              , "s", lambda: command.run("sort_size")),
    ("size reverse"      , "S", lambda: command.run("sort_size_rev")),
    ("time"              , "t", lambda: command.run("sort_time")),
    ("time reverse"      , "T", lambda: command.run("sort_time_rev")),
    ("link"              , "l", lambda: command.run("sort_nlink")),
    ("link reverse"      , "L", lambda: command.run("sort_nlink_rev")),
    ("permission"        , "p", lambda: command.run("sort_permission")),
    ("permission reverse", "P", lambda: command.run("sort_permission_rev")),
    ("toggle upward directory", "u", lambda: command.run("toggle_sort_updir")),
    ))

# The editor launcher example.
pyful.menu.define_menu("editor", (
    ("emacs"              , "e", lambda: process.spawn("emacs -nw %f")),
    ("emacs new terminal" , "E", lambda: process.spawn("emacs -nw %f %T")),
    ("emacs frame"        , "f", lambda: process.spawn("emacs %f")),
    ("vim"                , "v", lambda: process.spawn("vim %f")),
    ("vim new terminal"   , "V", lambda: process.spawn("vim %f %T")),
    ("gvim"               , "g", lambda: process.spawn("gvim %f %&")),
    ))

# The web broweser launcher example.
pyful.menu.define_menu("webbrowser", (
    ("firefox" , "f", lambda: process.spawn("firefox %&")),
    ("w3m"     , "w", lambda: process.spawn("w3m google.com %T")),
    ("chrome"  , "c", lambda: process.spawn("chromium-browser %&")),
    ))

# The file manager launcher example.
pyful.menu.define_menu("filemanager", (
    ("nautilus" , "n", lambda: process.spawn("nautilus --no-desktop %D %&")),
    ("mc"       , "m", lambda: process.spawn("mc %T")),
    ("thunar"   , "t", lambda: process.spawn("thunar %&")),
    ))

# The program launcher example.
pyful.menu.define_menu("launcher", (
    ("htop"           , "h", lambda: process.spawn("htop %T")),
    ("mc"             , "m", lambda: process.spawn("mc %T")),
    ("MOC"            , "M", lambda: process.spawn("mocp %T")),
    ("firefox"        , "f", lambda: process.spawn("firefox %&")),
    ("thunderbird"    , "T", lambda: process.spawn("thunderbird %&")),
    ("amarok"         , "a", lambda: process.spawn("amarok %&")),
    ("gimp"           , "g", lambda: process.spawn("gimp %&")),
    ("terminator"     , "t", lambda: process.spawn("terminator %&")),
    ("nautilus"       , "n", lambda: process.spawn("nautilus --no-desktop %D %&")),
    ("system-monitor" , "s", lambda: process.spawn("gnome-system-monitor %&")),
    ("synaptic"       , "S", lambda: process.spawn("gksu synaptic %&")),
    ))

# Update the filer keymap.
pyful.widget.define_key(widgets.filer, {
        "<f1>" : lambda: widgets.menu.show("File"),
        "<f2>" : lambda: widgets.menu.show("Edit"),
        "<f3>" : lambda: widgets.menu.show("View"),
        "<f4>" : lambda: widgets.menu.show("Go"),
        "<f5>" : lambda: widgets.menu.show("Tool"),
        "<f6>" : lambda: widgets.menu.show("Help"),
        "C-x"  : lambda: widgets.menu.show("Main"),
        "V"    : lambda: widgets.menu.show("fileinfo"),
        "s"    : lambda: widgets.menu.show("sort"),
        "L"    : lambda: widgets.menu.show("layout"),
        "E"    : lambda: widgets.menu.show("editor"),
        ";"    : lambda: widgets.menu.show("launcher"),
        })

# ======================================================================
# The file association example.
#
# The following macros do special behavior in the string passed to the
# process:
# 
#     %& -> The string passed to the process is evaluated on the
#           background through the shell;
#     %T -> The string passed to the process is process executed on
#           the external terminal;
#     %q -> Doesn't wait of the user input after the string passed to
#           the process is evaluated;
#     %f -> This macro is expanded to the file name to under the cursor;
#     %F -> This macro is expanded to the absolute path of file to
#           under the cursor;
#     %x -> This macro is expanded to the file name to under the
#           cursor that removed the extension;
#     %X -> This macro is expanded to the absolute path of file to
#           under the cursor that removed the extension;
#     %d -> This macro is expanded to the current directory name;
#     %D -> This macro is expanded to the absolute path of current
#           directory;
#     %d2 -> This macro is expanded to the next directory name;
#     %D2 -> This macro is expanded to the absolute path of next
#            directory;
#     %m -> This macro is expanded to the string that the mark files
#           name in the current directory is split by the space;
#     %M -> This macro is expanded to the string that the absolute
#           path of mark files in the current directory is split by
#           the space.
#
# ======================================================================

# Define a image file associate the menu item.
pyful.menu.define_menu("image", (
    ("display"    , "d", lambda: process.spawn("display %f %&")),
    ("gimp"       , "g", lambda: process.spawn("gimp %f %&")),
    ))

# Define a music file associate the menu item.
pyful.menu.define_menu("music", (
    ("mplayer"  , "m", lambda: process.spawn("mplayer %m")),
    ("MOC"      , "M", lambda: process.spawn("mocp -a %m %&")),
    ("amarok"   , "a", lambda: process.spawn("amarok %f %&")),
    ))

# Define a video file associate the menu item.
pyful.menu.define_menu("video", (
    ("mplayer"  , "m", lambda: process.spawn("mplayer %f")),
    ("vlc"      , "v", lambda: process.spawn("vlc %f %&")),
    ))

# Update filer keymap for file association.
pyful.widget.define_key(widgets.filer, {
        ("RET", ".py"   ): lambda: widgets.cmdline.shell("python %f"),
        ("RET", ".rb"   ): lambda: widgets.cmdline.shell("ruby %f"),
        ("RET", ".sh"   ): lambda: widgets.cmdline.shell("sh %f"),
        ("RET", ".exe"  ): lambda: widgets.cmdline.shell("wine %f"),
        ("RET", ".c"    ): lambda: widgets.cmdline.shell("gcc %f"),
        ("RET", ".java" ): lambda: widgets.cmdline.shell("javac %f"),
        ("RET", ".class"): lambda: widgets.cmdline.shell("java %x"),
        ("RET", ".jar"  ): lambda: widgets.cmdline.shell("java -jar %f"),
        ("RET", ".jpg"  ): lambda: widgets.menu.show("image"),
        ("RET", ".gif"  ): lambda: widgets.menu.show("image"),
        ("RET", ".png"  ): lambda: widgets.menu.show("image"),
        ("RET", ".bmp"  ): lambda: widgets.menu.show("image"),
        ("RET", ".mp3"  ): lambda: widgets.menu.show("music"),
        ("RET", ".flac" ): lambda: widgets.menu.show("music"),
        ("RET", ".avi"  ): lambda: widgets.menu.show("video"),
        ("RET", ".mp4"  ): lambda: widgets.menu.show("video"),
        ("RET", ".flv"  ): lambda: widgets.menu.show("video"),
        })


if "screen" in os.getenv("TERM"):
    # Change GNU SCREEN's title.
    sys.stdout.write("\033kpyful\033\\")
else:
    # Change terminal emulator's title.
    import socket
    sys.stdout.write("\033]0;pyful@{0}\007".format(socket.gethostname()))
