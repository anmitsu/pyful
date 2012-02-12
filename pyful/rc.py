# coding: utf-8
#
# pyful configure file.
# This file is executed in the local namespace and not generate module.
#

import pyful

# Set environments of pyful.
pyful.Pyful.environs["EDITOR"] = "vim"
pyful.Pyful.environs["PAGER"] = "lv"

# Set proc attributes.
pyful.process.Process.shell = ("/bin/bash", "-c")
pyful.process.Process.terminal_emulator = ("x-terminal-emulator", "-e")

# Set screen command and arguments.
#     {TITLE} is replaced to window title in screen.
#     {COMMAND} is replaced to a command in screen.
import os
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
#
#     "Tile"
#     "TileLeft"
#     "TileTop"
#     "TileBottom"
#     "Oneline"
#     "Onecolumn"
#     "Magnifier"
#     "Fullscreen"
#
pyful.filer.Workspace.layout = "Tile"

# Set default kind of sorting in directory.
#
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
#
pyful.filer.Directory.sort_kind = "Name[^]"

# Is a directory sorted in upwards?
pyful.filer.Directory.sort_updir = False

# Set scroll type in directory.
#
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
#
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
#
#     "default"
#     "midnight"
#     "dark"
#     "light"
#
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
#
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
#
pyful.widget.listbox.ListBox.scroll_type = "HalfScroll"

# Enable mouse support?
pyful.widget.ui.MouseHandler.enable(False)


# Set cmdline attributes.
pyful.cmdline.History.maxsave = 10000
pyful.cmdline.Clipboard.maxsave = 100


# Import very useful module.
from pyful import command, process

# Get very useful widgets.
filer = pyful.widget.get("Filer")
cmdline = pyful.widget.get("Cmdline")
menu = pyful.widget.get("Menu")

# Registration of program initialization.
# Pyful.atinit() wraps the initialization functions.
#
@pyful.Pyful.atinit
def myatinit():
    filer.loadfile("~/.pyfulinfo.json")
    cmdline.clipboard.loadfile("~/.pyful/clipboard")
    cmdline.history.loadfile("~/.pyful/history/shell", "Shell")
    cmdline.history.loadfile("~/.pyful/history/eval", "Eval")
    cmdline.history.loadfile("~/.pyful/history/mx", "Mx")
    cmdline.history.loadfile("~/.pyful/history/replace", "Replace")

# Registration of program termination.
# Pyful.atexit() wraps the termination functions.
#
@pyful.Pyful.atexit
def myatexit():
    filer.savefile("~/.pyfulinfo.json")
    cmdline.clipboard.savefile("~/.pyful/clipboard")
    cmdline.history.savefile("~/.pyful/history/shell", "Shell")
    cmdline.history.savefile("~/.pyful/history/eval", "Eval")
    cmdline.history.savefile("~/.pyful/history/mx", "Mx")
    cmdline.history.savefile("~/.pyful/history/replace", "Replace")

# Define the keymap of pyful.
#
# A key of the keymap dictionary is key or (key, ext).
# A value of the keymap dictionary is the callable function of no argument.
#
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
#

filer.keybind(
    lambda filer: {
        "M-1"           : lambda: filer.focus_workspace(0),
        "M-2"           : lambda: filer.focus_workspace(1),
        "M-3"           : lambda: filer.focus_workspace(2),
        "M-4"           : lambda: filer.focus_workspace(3),
        "M-5"           : lambda: filer.focus_workspace(4),
        "M-!"           : lambda: filer.mvdir_workspace_to(0),
        'M-"'           : lambda: filer.mvdir_workspace_to(1),
        "M-#"           : lambda: filer.mvdir_workspace_to(2),
        "M-$"           : lambda: filer.mvdir_workspace_to(3),
        "M-%"           : lambda: filer.mvdir_workspace_to(4),
        "M-f"           : command.query("switch_next_workspace"),
        "M-b"           : command.query("switch_prev_workspace"),
        "M-F"           : command.query("swap_workspace_inc"),
        "M-B"           : command.query("swap_workspace_dec"),
        "C-i"           : command.query("focus_next_dir"),
        "C-f"           : command.query("focus_next_dir"),
        "C-b"           : command.query("focus_prev_dir"),
        "<right>"       : command.query("focus_next_dir"),
        "<left>"        : command.query("focus_prev_dir"),
        "F"             : command.query("swap_dir_inc"),
        "B"             : command.query("swap_dir_dec"),
        "M-C-j"         : command.query("create_dir"),
        "M-C"           : command.query("close_dir"),
        "C-w"           : command.query("close_dir"),
        "C-l"           : command.query("all_reload"),
        "C-n"           : command.query("filer_cursor_down"),
        "<down>"        : command.query("filer_cursor_down"),
        "C-p"           : command.query("filer_cursor_up"),
        "<up>"          : command.query("filer_cursor_up"),
        "C-d"           : lambda: filer.dir.mvcursor(+5),
        "C-u"           : lambda: filer.dir.mvcursor(-5),
        "M-n"           : command.query("filer_scroll_down"),
        "M-p"           : command.query("filer_scroll_up"),
        "C-v"           : command.query("filer_pagedown"),
        "<npage>"       : command.query("filer_pagedown"),
        "M-v"           : command.query("filer_pageup"),
        "<ppage>"       : command.query("filer_pageup"),
        "C-a"           : command.query("filer_settop"),
        "M-<"           : command.query("filer_settop"),
        "C-e"           : command.query("filer_setbottom"),
        "M->"           : command.query("filer_setbottom"),
        "C-g"           : command.query("filer_reset"),
        "ESC"           : command.query("filer_reset"),
        "M-w"           : command.query("switch_workspace"),
        "M-h"           : command.query("chdir_backward"),
        "M-l"           : command.query("chdir_forward"),
        "C-h"           : command.query("chdir_parent"),
        "<backspace>"   : command.query("chdir_parent"),
        "~"             : command.query("chdir_home"),
        "\\"            : command.query("chdir_root"),
        "w"             : command.query("chdir_neighbor"),
        "f"             : command.query("finder_start"),
        "/"             : command.query("finder_start"),
        "v"             : command.query("fileviewer"),
        "P"             : command.query("pack"),
        "U"             : command.query("unpack2"),
        "u"             : command.query("unpack"),
        "J"             : command.query("drivejump"),
        "<end>"         : command.query("mark_toggle_all"),
        "SPC"           : command.query("mark_toggle"),
        "C-r"           : command.query("refresh_window"),
        "RET"           : command.query("open_at_system"),
        "C-j"           : command.query("open_at_system"),
        "e"             : command.query("spawn_editor"),
        ":"             : command.query("spawn_shell"),
        "h"             : command.query("shell"),
        "M-:"           : command.query("eval"),
        "M-x"           : command.query("mx"),
        "K"             : command.query("kill_thread"),
        "?"             : command.query("help"),
        "M-?"           : command.query("help_all"),
        "c"             : command.query("copy"),
        "<dc>"          : command.query("delete"),
        "D"             : command.query("delete"),
        "k"             : command.query("mkdir"),
        "m"             : command.query("move"),
        "n"             : command.query("newfile"),
        "r"             : command.query("rename"),
        "R"             : command.query("replace"),
        "l"             : command.query("symlink"),
        "d"             : command.query("trashbox"),
        "t"             : command.query("utime"),
        "x"             : command.query("enter_exec"),
        "*"             : command.query("mark"),
        "+"             : command.query("mask"),
        "Q"             : command.query("exit"),
        ("RET", ".dir" ): command.query("enter_dir"),
        ("RET", ".mark"): command.query("enter_mark"),
        ("RET", ".link"): command.query("enter_link"),
        ("RET", ".exec"): command.query("enter_exec"),
        ("RET", ".tar" ): command.query("untar"),
        ("RET", ".tgz" ): command.query("untar"),
        ("RET", ".gz"  ): command.query("untar"),
        ("RET", ".bz2" ): command.query("untar"),
        ("RET", ".zip" ): command.query("unzip"),
        ("RET", ".list"): command.query("enter_listfile"),
        })

filer.finder.keybind(
    lambda finder: {
        "M-n"         : lambda: finder.history_select(-1),
        "M-p"         : lambda: finder.history_select(+1),
        "C-g"         : lambda: finder.finish(),
        "ESC"         : lambda: finder.finish(),
        "C-c"         : lambda: finder.finish(),
        "C-h"         : lambda: finder.delete_backward_char(),
        "<backspace>" : lambda: finder.delete_backward_char(),
        })

cmdline.keybind(
    lambda cmdline: {
        "C-f"         : lambda: cmdline.forward_char(),
        "<right>"     : lambda: cmdline.forward_char(),
        "C-b"         : lambda: cmdline.backward_char(),
        "<left>"      : lambda: cmdline.backward_char(),
        "M-f"         : lambda: cmdline.forward_word(),
        "M-b"         : lambda: cmdline.backward_word(),
        "C-d"         : lambda: cmdline.delete_char(),
        "<dc>"        : lambda: cmdline.delete_char(),
        "C-h"         : lambda: cmdline.delete_backward_char(),
        "<backspace>" : lambda: cmdline.delete_backward_char(),
        "M-d"         : lambda: cmdline.delete_forward_word(),
        "M-h"         : lambda: cmdline.delete_backward_word(),
        "C-w"         : lambda: cmdline.delete_backward_word(),
        "C-k"         : lambda: cmdline.kill_line(),
        "C-u"         : lambda: cmdline.kill_line_all(),
        "C-a"         : lambda: cmdline.settop(),
        "C-e"         : lambda: cmdline.setbottom(),
        "C-g"         : lambda: cmdline.escape(),
        "C-c"         : lambda: cmdline.escape(),
        "ESC"         : lambda: cmdline.escape(),
        "RET"         : lambda: cmdline.execute(),
        "M-i"         : lambda: cmdline.select_action(),
        "M-m"         : lambda: cmdline.expandmacro(),
        "C-y"         : lambda: cmdline.clipboard.paste(),
        "M-y"         : lambda: cmdline.clipboard.start(),
        "C-i"         : lambda: cmdline.completion.start(),
        "M-j"         : lambda: cmdline.output.communicate(),
        "C-n"         : lambda: cmdline.history.mvcursor(+1),
        "<down>"      : lambda: cmdline.history.mvcursor(+1),
        "C-p"         : lambda: cmdline.history.mvcursor(-1),
        "<up>"        : lambda: cmdline.history.mvcursor(-1),
        "M-n"         : lambda: cmdline.history.mvscroll(+1),
        "M-p"         : lambda: cmdline.history.mvscroll(-1),
        "C-v"         : lambda: cmdline.history.pagedown(),
        "M-v"         : lambda: cmdline.history.pageup(),
        "M-<"         : lambda: cmdline.history.settop(),
        "M->"         : lambda: cmdline.history.setbottom(),
        "C-x"         : lambda: cmdline.history.delete(),
        "M-+"         : lambda: cmdline.history.zoombox(+5),
        "M--"         : lambda: cmdline.history.zoombox(-5),
        "M-="         : lambda: cmdline.history.zoombox(0),
        })

cmdline.clipboard.keybind(
    lambda clipboard: {
        "C-n"         : lambda: clipboard.mvcursor(1),
        "<down>"      : lambda: clipboard.mvcursor(1),
        "C-v"         : lambda: clipboard.pagedown(),
        "C-d"         : lambda: clipboard.pagedown(),
        "C-p"         : lambda: clipboard.mvcursor(-1),
        "<up>"        : lambda: clipboard.mvcursor(-1),
        "M-v"         : lambda: clipboard.pageup(),
        "C-u"         : lambda: clipboard.pageup(),
        "M-n"         : lambda: clipboard.mvscroll(+1),
        "M-p"         : lambda: clipboard.mvscroll(-1),
        "C-x"         : lambda: clipboard.delete(),
        "C-g"         : lambda: clipboard.finish(),
        "C-c"         : lambda: clipboard.finish(),
        "ESC"         : lambda: clipboard.finish(),
        "RET"         : lambda: clipboard.insert(),
        "M-+"         : lambda: clipboard.zoombox(+5),
        "M--"         : lambda: clipboard.zoombox(-5),
        "M-="         : lambda: clipboard.zoombox(0),
        "C-f"         : lambda: clipboard.textbox.forward_char(),
        "<right>"     : lambda: clipboard.textbox.forward_char(),
        "C-b"         : lambda: clipboard.textbox.backward_char(),
        "<left>"      : lambda: clipboard.textbox.backward_char(),
        "M-f"         : lambda: clipboard.textbox.forward_word(),
        "M-b"         : lambda: clipboard.textbox.backward_word(),
        "C-d"         : lambda: clipboard.textbox.delete_char(),
        "<dc>"        : lambda: clipboard.textbox.delete_char(),
        "C-h"         : lambda: clipboard.textbox.delete_backward_char(),
        "<backspace>" : lambda: clipboard.textbox.delete_backward_char(),
        "M-d"         : lambda: clipboard.textbox.delete_forward_word(),
        "M-h"         : lambda: clipboard.textbox.delete_backward_word(),
        "C-w"         : lambda: clipboard.textbox.delete_backward_word(),
        "C-k"         : lambda: clipboard.textbox.kill_line(),
        "C-u"         : lambda: clipboard.textbox.kill_line_all(),
        "C-a"         : lambda: clipboard.textbox.settop(),
        "C-e"         : lambda: clipboard.textbox.setbottom(),
        })

cmdline.completion.keybind(
    lambda completion: {
        "C-n"     : lambda: completion.cursordown(),
        "<down>"  : lambda: completion.cursordown(),
        "C-p"     : lambda: completion.cursorup(),
        "<up>"    : lambda: completion.cursorup(),
        "C-i"     : lambda: completion.mvcursor(+1),
        "C-f"     : lambda: completion.mvcursor(+1),
        "<right>" : lambda: completion.mvcursor(+1),
        "C-b"     : lambda: completion.mvcursor(-1),
        "<left>"  : lambda: completion.mvcursor(-1),
        "M-n"     : lambda: completion.mvscroll(+1),
        "M-p"     : lambda: completion.mvscroll(-1),
        "C-v"     : lambda: completion.pagedown(),
        "M-v"     : lambda: completion.pageup(),
        "C-g"     : lambda: completion.finish(),
        "C-c"     : lambda: completion.finish(),
        "ESC"     : lambda: completion.finish(),
        "RET"     : lambda: completion.insert(),
        "M-+"     : lambda: completion.zoombox(+5),
        "M--"     : lambda: completion.zoombox(-5),
        "M-="     : lambda: completion.zoombox(0),
        })

cmdline.output.keybind(
    lambda output: {
        "C-n"    : lambda: output.mvcursor(1),
        "<down>" : lambda: output.mvcursor(1),
        "C-v"    : lambda: output.pagedown(),
        "C-d"    : lambda: output.pagedown(),
        "C-p"    : lambda: output.mvcursor(-1),
        "<up>"   : lambda: output.mvcursor(-1),
        "M-v"    : lambda: output.pageup(),
        "C-u"    : lambda: output.pageup(),
        "M-n"    : lambda: output.mvscroll(+1),
        "M-p"    : lambda: output.mvscroll(-1),
        "C-g"    : lambda: output.finish(),
        "C-c"    : lambda: output.finish(),
        "ESC"    : lambda: output.finish(),
        "RET"    : lambda: output.edit(),
        "M-+"    : lambda: output.zoombox(+5),
        "M--"    : lambda: output.zoombox(-5),
        "M-="    : lambda: output.zoombox(0),
        })

pyful.widget.get("Help").keybind(
    lambda helper: {
        "j"      : lambda: helper.mvcursor(1),
        "C-n"    : lambda: helper.mvcursor(1),
        "<down>" : lambda: helper.mvcursor(1),
        "k"      : lambda: helper.mvcursor(-1),
        "C-p"    : lambda: helper.mvcursor(-1),
        "<up>"   : lambda: helper.mvcursor(-1),
        "C-v"    : lambda: helper.pagedown(),
        "C-d"    : lambda: helper.pagedown(),
        "M-v"    : lambda: helper.pageup(),
        "C-u"    : lambda: helper.pageup(),
        "M-n"    : lambda: helper.mvscroll(+1),
        "M-p"    : lambda: helper.mvscroll(-1),
        "C-g"    : lambda: helper.hide(),
        "C-c"    : lambda: helper.hide(),
        "ESC"    : lambda: helper.hide(),
        "M-+"    : lambda: helper.zoombox(+5),
        "M--"    : lambda: helper.zoombox(-5),
        "M-="    : lambda: helper.zoombox(0),
    })

pyful.widget.get("ActionBox").keybind(
    lambda actionbox: {
        "C-n"    : lambda: actionbox.mvcursor(1),
        "<down>" : lambda: actionbox.mvcursor(1),
        "C-v"    : lambda: actionbox.pagedown(),
        "C-d"    : lambda: actionbox.pagedown(),
        "C-p"    : lambda: actionbox.mvcursor(-1),
        "<up>"   : lambda: actionbox.mvcursor(-1),
        "M-n"    : lambda: actionbox.mvscroll(1),
        "M-p"    : lambda: actionbox.mvscroll(-1),
        "M-v"    : lambda: actionbox.pageup(),
        "C-u"    : lambda: actionbox.pageup(),
        "C-g"    : lambda: actionbox.hide(),
        "C-c"    : lambda: actionbox.hide(),
        "ESC"    : lambda: actionbox.hide(),
        "M-+"    : lambda: actionbox.zoombox(+5),
        "M--"    : lambda: actionbox.zoombox(-5),
        "M-="    : lambda: actionbox.zoombox(0),
        "RET"    : lambda: actionbox.select_action(),
        })

pyful.widget.get("ConfirmBox").keybind(
    lambda confirmbox: {
        "C-f"     : lambda: confirmbox.mvcursor(1),
        "<right>" : lambda: confirmbox.mvcursor(1),
        "C-b"     : lambda: confirmbox.mvcursor(-1),
        "<left>"  : lambda: confirmbox.mvcursor(-1),
        "C-a"     : lambda: confirmbox.settop(),
        "C-e"     : lambda: confirmbox.setbottom(),
        "C-c"     : lambda: confirmbox.hide(),
        "C-g"     : lambda: confirmbox.hide(),
        "ESC"     : lambda: confirmbox.hide(),
        "RET"     : lambda: confirmbox.get_result(),
        "C-n"     : lambda: confirmbox.listbox.mvcursor(1),
        "<down>"  : lambda: confirmbox.listbox.mvcursor(1),
        "C-p"     : lambda: confirmbox.listbox.mvcursor(-1),
        "<up>"    : lambda: confirmbox.listbox.mvcursor(-1),
        "M-n"     : lambda: confirmbox.listbox.mvscroll(1),
        "M-p"     : lambda: confirmbox.listbox.mvscroll(-1),
        "C-v"     : lambda: confirmbox.listbox.pagedown(),
        "M-v"     : lambda: confirmbox.listbox.pageup(),
        "M-+"     : lambda: confirmbox.listbox.zoombox(+5),
        "M--"     : lambda: confirmbox.listbox.zoombox(-5),
        "M-="     : lambda: confirmbox.listbox.zoombox(0),
        })

menu.keybind(
    lambda menu: {
        "C-n"    : lambda: menu.mvcursor(+1),
        "<down>" : lambda: menu.mvcursor(+1),
        "C-p"    : lambda: menu.mvcursor(-1),
        "<up>"   : lambda: menu.mvcursor(-1),
        "C-d"    : lambda: menu.mvcursor(+5),
        "C-u"    : lambda: menu.mvcursor(-5),
        "C-v"    : lambda: menu.pagedown(),
        "M-v"    : lambda: menu.pageup(),
        "M-n"    : lambda: menu.mvscroll(+1),
        "M-p"    : lambda: menu.mvscroll(-1),
        "C-a"    : lambda: menu.settop(),
        "M-<"    : lambda: menu.settop(),
        "C-e"    : lambda: menu.setbottom(),
        "M->"    : lambda: menu.setbottom(),
        "C-g"    : lambda: menu.hide(),
        "C-c"    : lambda: menu.hide(),
        "ESC"    : lambda: menu.hide(),
        "RET"    : lambda: menu.run(),
        })

# Define the menu.
#
# A key of the menu item dictionary is the menu title.
#
# A value of the menu item dictionary must be the sequence that consist of
# the sequence that meet the following requirement:
#     - The first element is the menu item title;
#     - The second element is the key symbol;
#     - The third element is the callable function of no argument.
#
menu.items["filer"] = (
    ("toggle (e)xtension" , "e", command.query("toggle_draw_ext")),
    ("toggle (p)ermission", "p", command.query("toggle_draw_permission")),
    ("toggle n(l)ink"     , "l", command.query("toggle_draw_nlink")),
    ("toggle (u)ser"      , "u", command.query("toggle_draw_user")),
    ("toggle (g)roup"     , "g", command.query("toggle_draw_group")),
    ("toggle (s)ize"      , "s", command.query("toggle_draw_size")),
    ("toggle m(t)ime"     , "t", command.query("toggle_draw_mtime")),
    )

menu.items["layout"] = (
    ("(t)ile"        , "t", command.query("layout_tile")),
    ("tile(L)eft"    , "L", command.query("layout_tileleft")),
    ("tile(T)op"     , "T", command.query("layout_tiletop")),
    ("tile(B)ottom"  , "B", command.query("layout_tilebottom")),
    ("one(l)ine"     , "l", command.query("layout_oneline")),
    ("one(c)olumn"   , "c", command.query("layout_onecolumn")),
    ("(m)agnifier"   , "m", command.query("layout_magnifier")),
    ("(f)ullscreen"  , "f", command.query("layout_fullscreen")),
    )

menu.items["sort"] = (
    ("(n)ame"              , "n", command.query("sort_name")),
    ("(N)ame reverse"      , "N", command.query("sort_name_rev")),
    ("(e)xtension"         , "e", command.query("sort_ext")),
    ("(E)xtension reverse" , "E", command.query("sort_ext_rev")),
    ("(s)ize"              , "s", command.query("sort_size")),
    ("(S)ize reverse"      , "S", command.query("sort_size_rev")),
    ("(t)ime"              , "t", command.query("sort_time")),
    ("(T)ime reverse"      , "T", command.query("sort_time_rev")),
    ("(l)ink"              , "l", command.query("sort_nlink")),
    ("(L)ink reverse"      , "L", command.query("sort_nlink_rev")),
    ("(p)ermission"        , "p", command.query("sort_permission")),
    ("(P)ermission reverse", "P", command.query("sort_permission_rev")),
    ("toggle (u)pward directory", "u", command.query("toggle_sort_updir")),
    )

# The editor launcher example.
menu.items["editor"] = (
    ("(e)macs"              , "e", lambda: process.spawn("emacs -nw %f")),
    ("(E)macs new terminal" , "E", lambda: process.spawn("emacs -nw %f %T")),
    ("emacs (f)rame"        , "f", lambda: process.spawn("emacs %f")),
    ("(v)im"                , "v", lambda: process.spawn("vim %f")),
    ("(V)im new terminal"   , "V", lambda: process.spawn("vim %f %T")),
    ("(g)vim"               , "g", lambda: process.spawn("gvim %f %&")),
    )

# The program launcher example.
menu.items["launcher"] = (
    ("(h)top"           , "h", lambda: process.spawn("htop %T")),
    ("(m)c"             , "m", lambda: process.spawn("mc %T")),
    ("(M)OC"            , "M", lambda: process.spawn("mocp %T")),
    ("(w)3m"            , "w", lambda: process.spawn("w3m google.com %T")),
    ("(f)irefox"        , "f", lambda: process.spawn("firefox %&")),
    ("(T)hunderbird"    , "T", lambda: process.spawn("thunderbird %&")),
    ("(a)marok"         , "a", lambda: process.spawn("amarok %&")),
    ("(g)imp"           , "g", lambda: process.spawn("gimp %&")),
    ("(t)erminator"     , "t", lambda: process.spawn("terminator %&")),
    ("(n)autilus"       , "n", lambda: process.spawn("nautilus --no-desktop %D %&")),
    ("(s)ystem-monitor" , "s", lambda: process.spawn("gnome-system-monitor %&")),
    ("(S)ynaptic"       , "S", lambda: process.spawn("gksu synaptic %&")),
    )

# Update the filer keymap.
filer.keymap.update({
        "V": lambda: menu.show("filer"),
        "s": lambda: menu.show("sort"),
        "L": lambda: menu.show("layout"),
        "E": lambda: menu.show("editor"),
        ";": lambda: menu.show("launcher"),
        })

# The file association example.
#
# The following macros do special behavior in the string passed to the process:
#     %& -> The string passed to the process is
#           evaluated on the background through the shell;
#     %T -> The string passed to the process is process
#           executed on the external terminal;
#     %q -> Doesn't wait of the user input after
#           the string passed to the process is evaluated;
#
#     %f -> This macro is expanded to the file name to under the cursor;
#     %F -> This macro is expanded to the absolute path of
#           file to under the cursor;
#
#     %x -> This macro is expanded to the file name to
#           under the cursor that removed the extension;
#     %X -> This macro is expanded to the absolute path of file to
#           under the cursor that removed the extension;
#
#     %d -> This macro is expanded to the current directory name;
#     %D -> This macro is expanded to the absolute path of
#           current directory;
#
#     %d2 -> This macro is expanded to the next directory name;
#     %D2 -> This macro is expanded to the absolute path of
#            next directory;
#
#     %m -> This macro is expanded to the string that the mark files name in
#           the current directory is split by the space;
#     %M -> This macro is expanded to the string that the absolute path of
#           mark files in the current directory is split by the space.
#

# Define a image file associate the menu item.
menu.items["image"] = (
    ("(d)isplay"    , "d", lambda: process.spawn("display %f %&")),
    ("(g)imp"       , "g", lambda: process.spawn("gimp %f %&")),
    )

# Define a music file associate the menu item.
menu.items["music"] = (
    ("(m)player"  , "m", lambda: process.spawn("mplayer %m")),
    ("(M)OC"      , "M", lambda: process.spawn("mocp -a %m %&")),
    ("(a)marok"   , "a", lambda: process.spawn("amarok %f %&")),
    )

# Define a video file associate the menu item.
menu.items["video"] = (
    ("(m)player"  , "m", lambda: process.spawn("mplayer %f")),
    ("(v)lc"      , "v", lambda: process.spawn("vlc %f %&")),
    )

myassociation = {
    ("RET", ".py"   ): lambda: cmdline.shell("python %f"),
    ("RET", ".rb"   ): lambda: cmdline.shell("ruby %f"),
    ("RET", ".sh"   ): lambda: cmdline.shell("sh %f"),
    ("RET", ".exe"  ): lambda: cmdline.shell("wine %f"),
    ("RET", ".c"    ): lambda: cmdline.shell("gcc %f"),
    ("RET", ".java" ): lambda: cmdline.shell("javac %f"),
    ("RET", ".class"): lambda: cmdline.shell("java %x"),
    ("RET", ".jar"  ): lambda: cmdline.shell("java -jar %f"),
    ("RET", ".jpg"  ): lambda: menu.show("image"),
    ("RET", ".gif"  ): lambda: menu.show("image"),
    ("RET", ".png"  ): lambda: menu.show("image"),
    ("RET", ".bmp"  ): lambda: menu.show("image"),
    ("RET", ".mp3"  ): lambda: menu.show("music"),
    ("RET", ".flac" ): lambda: menu.show("music"),
    ("RET", ".avi"  ): lambda: menu.show("video"),
    ("RET", ".mp4"  ): lambda: menu.show("video"),
    ("RET", ".flv"  ): lambda: menu.show("video"),
    }

filer.keymap.update(myassociation)

import sys
if "screen" in os.getenv("TERM"):
    # Change GNU SCREEN's title.
    sys.stdout.write("\033kpyful\033\\")
else:
    # Change terminal emulator's title.
    import socket
    sys.stdout.write("\033]0;pyful@{0}\007".format(socket.gethostname()))
