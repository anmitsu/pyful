# coding: utf-8
#
# pyful configure file.
# This file is executed in the local namespace and not generate module.
#

from pyful import Pyful
from pyful import look
from pyful import message
from pyful import mode
from pyful import process
from pyful import ui
from pyful.command import commands
from pyful.filer import Workspace, Directory, Finder, FileStat

# Get PYthon File management UtiLity.
filer = ui.getcomponent("Filer")
cmdline = ui.getcomponent("Cmdline")
menu = ui.getcomponent("Menu")

# Set environments of pyful.
Pyful.environs["EDITOR"] = "vim"
Pyful.environs["PAGER"] = "less"

# Set proc attributes.
process.Process.shell = ("/bin/bash", "-c")
process.Process.terminal_emulator = ("x-terminal-emulator", "-e")

# Set cmdline attributes.
cmdline.history.maxsave = 10000
cmdline.clipboard.maxsave = 100

# Set the mode of mkdir and newfile in octal number.
mode.Mkdir.dirmode = 0o755
mode.Newfile.filemode = 0o644
mode.TrashBox.path = "~/.pyful/trashbox"

# Set the prompt of shell mode.
mode.Shell.prompt = "$"

# Set message history.
message.Message.history = 100

# Set height of message box.
message.MessageBox.height = 4

# Set the default path of the directory creating.
Workspace.default_path = "~/"

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
Workspace.layout = "Tile"

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
Directory.sort_kind = "Name[^]"

# Set scroll type in directory.
#
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
#
Directory.scroll_type = "HalfScroll"

# Set statusbar format in directory.
Directory.statusbar_format = " [{MARK}/{FILE}] {MARKSIZE}bytes {SCROLL}({CURSOR}) {SORT} "

# Distinguish upper case and lower case at a finder?
Finder.smartcase = True

# Set PyMigemo and migemo dictionary.
# It is necessary to install PyMigemo to use migemo.
try:
    import migemo
    Finder.migemo = migemo.Migemo("/usr/share/cmigemo/utf-8/migemo-dict")
except (ImportError, ValueError):
    Finder.migemo = None

# Set the time format of file.
# It conforms to the strftime format from time module.
FileStat.time_format = "%y-%m-%d %H:%M"
# FileStat.time_format = "%c(%a)"

# Set the flag of file modified within 24 hours.
FileStat.time_24_flag = "!"
# Set the flag of file modified within a week.
FileStat.time_week_flag = "#"
# Set the flag of file modified more in old time.
FileStat.time_yore_flag = " "

# Display the file extension?
FileStat.view_ext = False
# Display the file permission?
FileStat.view_permission = False
# Display the number of link?
FileStat.view_nlink = False
# Display the user name of file?
FileStat.view_user = False
# Display the group name of file?
FileStat.view_group = False
# Display the file size?
FileStat.view_size = True
# Display the change time of file?
FileStat.view_mtime = True

# Set my look.
#
#     "default"
#     "midnight"
#     "dark"
#     "light"
#
look.Look.mylook = "default"

# Set borders.
# Smooth borders:
ui.StandardScreen.borders = []
ui.InfoBox.borders = []
# Classical borders:
# ui.StandardScreen.borders = ["|", "|", "-", "-", "+", "+", "+", "+"]
# ui.InfoBox.borders = ["|", "|", "-", "-", "+", "+", "+", "+"]

# Set zoom attribute of infobox.
# Infobox is an area displaying information of cmdline and message.
ui.InfoBox.zoom = 0

# Set scroll type in infobox.
#
#     "HalfScroll"
#     "PageScroll"
#     "ContinuousScroll"
#
ui.InfoBox.scroll_type = "HalfScroll"

# Registration of program initialization.
# Pyful.atinit() wraps the initialization functions.
#
@Pyful.atinit
def myatinit():
    filer.loadfile("~/.pyful/info")
    cmdline.clipboard.loadfile("~/.pyful/clipboard")
    cmdline.history.loadfile("~/.pyful/history/shell", "Shell")
    cmdline.history.loadfile("~/.pyful/history/eval", "Eval")
    cmdline.history.loadfile("~/.pyful/history/mx", "Mx")
    cmdline.history.loadfile("~/.pyful/history/replace", "Replace")

# Registration of program termination.
# Pyful.atexit() wraps the termination functions.
#
@Pyful.atexit
def myatexit():
    filer.savefile("~/.pyful/info")
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
#     "RET" -> Enter
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
#     "C-j", "C-m" are interpreted as "RET" in most terminals.
#
myfilerkeymap = {
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
    "M-f"           : commands["view_next_workspace"],
    "M-b"           : commands["view_prev_workspace"],
    "M-F"           : commands["swap_workspace_inc"],
    "M-B"           : commands["swap_workspace_dec"],
    "C-i"           : commands["focus_next_dir"],
    "C-f"           : commands["focus_next_dir"],
    "C-b"           : commands["focus_prev_dir"],
    "<right>"       : commands["focus_next_dir"],
    "<left>"        : commands["focus_prev_dir"],
    "F"             : commands["swap_dir_inc"],
    "B"             : commands["swap_dir_dec"],
    "M-RET"         : commands["create_dir"],
    "M-C"           : commands["close_dir"],
    "C-w"           : commands["close_dir"],
    "C-l"           : commands["all_reload"],
    "C-n"           : commands["filer_cursor_down"],
    "<down>"        : commands["filer_cursor_down"],
    "C-p"           : commands["filer_cursor_up"],
    "<up>"          : commands["filer_cursor_up"],
    "C-d"           : lambda: filer.dir.mvcursor(+5),
    "C-u"           : lambda: filer.dir.mvcursor(-5),
    "M-n"           : commands["filer_scroll_down"],
    "M-p"           : commands["filer_scroll_up"],
    "C-v"           : commands["filer_pagedown"],
    "<npage>"       : commands["filer_pagedown"],
    "M-v"           : commands["filer_pageup"],
    "<ppage>"       : commands["filer_pageup"],
    "C-a"           : commands["filer_settop"],
    "M-<"           : commands["filer_settop"],
    "C-e"           : commands["filer_setbottom"],
    "M->"           : commands["filer_setbottom"],
    "C-g"           : commands["filer_reset"],
    "ESC"           : commands["filer_reset"],
    "M-w"           : commands["switch_workspace"],
    "M-h"           : commands["chdir_backward"],
    "M-l"           : commands["chdir_forward"],
    "C-h"           : commands["chdir_parent"],
    "<backspace>"   : commands["chdir_parent"],
    "~"             : commands["chdir_home"],
    "\\"            : commands["chdir_root"],
    "w"             : commands["chdir_neighbor"],
    "f"             : commands["finder_start"],
    "/"             : commands["finder_start"],
    "v"             : commands["fileviewer"],
    "P"             : commands["pack"],
    "U"             : commands["unpack2"],
    "u"             : commands["unpack"],
    "J"             : commands["drivejump"],
    "<end>"         : commands["mark_toggle_all"],
    "SPC"           : commands["mark_toggle"],
    "C-r"           : commands["refresh_window"],
    "RET"           : commands["open_at_system"],
    "e"             : commands["spawn_editor"],
    ":"             : commands["spawn_shell"],
    "h"             : commands["shell"],
    "M-:"           : commands["eval"],
    "M-x"           : commands["mx"],
    "K"             : commands["kill_thread"],
    "?"             : commands["help"],
    "M-?"           : commands["help_all"],
    "c"             : commands["copy"],
    "<dc>"          : commands["delete"],
    "D"             : commands["delete"],
    "k"             : commands["mkdir"],
    "m"             : commands["move"],
    "n"             : commands["newfile"],
    "r"             : commands["rename"],
    "R"             : commands["replace"],
    "l"             : commands["symlink"],
    "d"             : commands["trashbox"],
    "t"             : commands["utime"],
    "x"             : commands["enter_exec"],
    "Q"             : commands["exit"],
    ("RET", ".dir" ): commands["enter_dir"],
    ("RET", ".mark"): commands["enter_mark"],
    ("RET", ".link"): commands["enter_link"],
    ("RET", ".exec"): commands["enter_exec"],
    ("RET", ".tar" ): commands["untar"],
    ("RET", ".tgz" ): commands["untar"],
    ("RET", ".gz"  ): commands["untar"],
    ("RET", ".bz2" ): commands["untar"],
    ("RET", ".zip" ): commands["unzip"],
    ("RET", ".list"): commands["enter_listfile"],
    }

myfinderkeymap = {
    "M-n"         : lambda: filer.finder.history_select(-1),
    "M-p"         : lambda: filer.finder.history_select(+1),
    "C-g"         : lambda: filer.finder.finish(),
    "ESC"         : lambda: filer.finder.finish(),
    "C-c"         : lambda: filer.finder.finish(),
    "C-h"         : lambda: filer.finder.delete_backward_char(),
    "<backspace>" : lambda: filer.finder.delete_backward_char(),
    }

mycmdlinekeymap = {
    "C-f"         : lambda: cmdline.forward_char(),
    "<right>"     : lambda: cmdline.forward_char(),
    "C-b"         : lambda: cmdline.backward_char(),
    "<left>"      : lambda: cmdline.backward_char(),
    "M-f"         : lambda: cmdline.forward_word(),
    "M-b"         : lambda: cmdline.backward_word(),
    "C-d"         : lambda: cmdline.delete_char(),
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
    "M-m"         : lambda: cmdline.expandmacro(),
    "C-y"         : lambda: cmdline.clipboard.paste(),
    "M-y"         : lambda: cmdline.clipboard.start(),
    "C-i"         : lambda: cmdline.completion.start(),
    "M-j"         : lambda: cmdline.output.infoarea(),
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
    "M-+"         : commands["zoom_in_infobox"],
    "M--"         : commands["zoom_out_infobox"],
    "M-="         : commands["zoom_normal_infobox"],
    }

myclipboardkeymap = {
    "C-n"    : lambda: cmdline.clipboard.mvcursor(1),
    "<down>" : lambda: cmdline.clipboard.mvcursor(1),
    "C-v"    : lambda: cmdline.clipboard.pagedown(),
    "C-d"    : lambda: cmdline.clipboard.pagedown(),
    "C-p"    : lambda: cmdline.clipboard.mvcursor(-1),
    "<up>"   : lambda: cmdline.clipboard.mvcursor(-1),
    "M-v"    : lambda: cmdline.clipboard.pageup(),
    "C-u"    : lambda: cmdline.clipboard.pageup(),
    "C-x"    : lambda: cmdline.clipboard.delete(),
    "C-g"    : lambda: cmdline.clipboard.finish(),
    "C-c"    : lambda: cmdline.clipboard.finish(),
    "ESC"    : lambda: cmdline.clipboard.finish(),
    "RET"    : lambda: cmdline.clipboard.insert(),
    }

mycompletionkeymap = {
    "C-n"     : lambda: cmdline.completion.cursordown(),
    "<down>"  : lambda: cmdline.completion.cursordown(),
    "C-p"     : lambda: cmdline.completion.cursorup(),
    "<up>"    : lambda: cmdline.completion.cursorup(),
    "C-i"     : lambda: cmdline.completion.mvcursor(+1),
    "C-f"     : lambda: cmdline.completion.mvcursor(+1),
    "<right>" : lambda: cmdline.completion.mvcursor(+1),
    "C-b"     : lambda: cmdline.completion.mvcursor(-1),
    "<left>"  : lambda: cmdline.completion.mvcursor(-1),
    "C-g"     : lambda: cmdline.completion.finish(),
    "C-c"     : lambda: cmdline.completion.finish(),
    "ESC"     : lambda: cmdline.completion.finish(),
    "RET"     : lambda: cmdline.completion.insert(),
    }

myoutputkeymap = {
    "C-n"    : lambda: cmdline.output.mvcursor(1),
    "<down>" : lambda: cmdline.output.mvcursor(1),
    "C-v"    : lambda: cmdline.output.pagedown(),
    "C-d"    : lambda: cmdline.output.pagedown(),
    "C-p"    : lambda: cmdline.output.mvcursor(-1),
    "<up>"   : lambda: cmdline.output.mvcursor(-1),
    "M-v"    : lambda: cmdline.output.pageup(),
    "C-u"    : lambda: cmdline.output.pageup(),
    "C-g"    : lambda: cmdline.output.finish(),
    "C-c"    : lambda: cmdline.output.finish(),
    "ESC"    : lambda: cmdline.output.finish(),
    "RET"    : lambda: cmdline.output.edit(),
    }

mymenukeymap = {
    "C-n"    : lambda: menu.mvcursor(+1),
    "<down>" : lambda: menu.mvcursor(+1),
    "C-p"    : lambda: menu.mvcursor(-1),
    "<up>"   : lambda: menu.mvcursor(-1),
    "C-d"    : lambda: menu.mvcursor(+5),
    "C-v"    : lambda: menu.mvcursor(+5),
    "C-u"    : lambda: menu.mvcursor(-5),
    "M-v"    : lambda: menu.mvcursor(-5),
    "C-g"    : lambda: menu.hide(),
    "C-c"    : lambda: menu.hide(),
    "ESC"    : lambda: menu.hide(),
    "RET"    : lambda: menu.run(),
    }

# Update the keymap of pyful.
Directory.keymap.update(myfilerkeymap)
Finder.keymap.update(myfinderkeymap)
cmdline.keymap.update(mycmdlinekeymap)
cmdline.clipboard.keymap.update(myclipboardkeymap)
cmdline.completion.keymap.update(mycompletionkeymap)
cmdline.output.keymap.update(myoutputkeymap)
menu.keymap.update(mymenukeymap)

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
    ("toggle (e)xtension" , "e", commands["toggle_view_ext"]),
    ("toggle (p)ermission", "p", commands["toggle_view_permission"]),
    ("toggle n(l)ink"     , "l", commands["toggle_view_nlink"]),
    ("toggle (u)ser"      , "u", commands["toggle_view_user"]),
    ("toggle (g)roup"     , "g", commands["toggle_view_group"]),
    ("toggle (s)ize"      , "s", commands["toggle_view_size"]),
    ("toggle m(t)ime"     , "t", commands["toggle_view_mtime"]),
    )

menu.items["layout"] = (
    ("(t)ile"        , "t", commands["layout_tile"]),
    ("tile(L)eft"    , "L", commands["layout_tileleft"]),
    ("tile(T)op"     , "T", commands["layout_tiletop"]),
    ("tile(B)ottom"  , "B", commands["layout_tilebottom"]),
    ("one(l)ine"     , "l", commands["layout_oneline"]),
    ("one(c)olumn"   , "c", commands["layout_onecolumn"]),
    ("(m)agnifier"   , "m", commands["layout_magnifier"]),
    ("(f)ullscreen"  , "f", commands["layout_fullscreen"]),
    )

menu.items["sort"] = (
    ("(n)ame"              , "n", commands["sort_name"]),
    ("(N)ame reverse"      , "N", commands["sort_name_rev"]),
    ("(e)xtension"         , "e", commands["sort_ext"]),
    ("(E)xtension reverse" , "E", commands["sort_ext_rev"]),
    ("(s)ize"              , "s", commands["sort_size"]),
    ("(S)ize reverse"      , "S", commands["sort_size_rev"]),
    ("(t)ime"              , "t", commands["sort_time"]),
    ("(T)ime reverse"      , "T", commands["sort_time_rev"]),
    ("(l)ink"              , "l", commands["sort_nlink"]),
    ("(L)ink reverse"      , "L", commands["sort_nlink_rev"]),
    ("(p)ermission"        , "p", commands["sort_permission"]),
    ("(P)ermission reverse", "P", commands["sort_permission_rev"]),
    )

menu.items["mark"] = (
    ("(r)egex mark", "r", commands["mark"]),
    ("(S)ource"    , "S", commands["mark_source"]),
    ("(A)rchive"   , "A", commands["mark_archive"]),
    ("(I)mage"     , "I", commands["mark_image"]),
    ("(M)usic"     , "M", commands["mark_music"]),
    ("(V)ideo"     , "V", commands["mark_video"]),
    ("mark (a)ll"  , "a", commands["mark_all"]),
    ("mark (c)lear", "c", commands["mark_clear"]),
    )

menu.items["mask"] = (
    ("(m)ask"   , "m", commands["mask"]),
    ("(S)ource" , "S", commands["mask_source"]),
    ("(A)rchive", "A", commands["mask_archive"]),
    ("(I)mage"  , "I", commands["mask_image"]),
    ("(M)usic"  , "M", commands["mask_music"]),
    ("(V)ideo"  , "V", commands["mask_video"]),
    ("(c)lear"  , "c", commands["mask_clear"]),
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
Directory.keymap.update({
        "V": lambda: menu.show("filer"),
        "s": lambda: menu.show("sort"),
        "L": lambda: menu.show("layout"),
        "*": lambda: menu.show("mark"),
        "+": lambda: menu.show("mask"),
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

Directory.keymap.update(myassociation)

import os, sys
if "screen" in os.getenv("TERM"):
    # Change GNU SCREEN's title.
    sys.stdout.write("\033kpyful\033\\")
else:
    # Change terminal emulator's title.
    import socket
    sys.stdout.write("\033]0;pyful@{0}\007".format(socket.gethostname()))
