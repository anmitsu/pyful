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
from pyful.keymap import *

# Get PYthon File management UtiLity.
filer = ui.getcomponent("Filer")
cmdline = ui.getcomponent("Cmdline")
menu = ui.getcomponent("Menu")

# Set environments of pyful.
Pyful.environs['EDITOR'] = 'vim'
Pyful.environs['PAGER'] = 'less'
Pyful.environs['TRASHBOX'] = '~/.pyful/trashbox'
Pyful.environs['LOOKS'] = look.looks['default']
# Pyful.environs['LOOKS'] = look.looks['midnight']

# Set proc attributes.
process.Process.shell = ('/bin/bash', '-c')
process.Process.terminal_emulator = ('x-terminal-emulator', '-e')

# Set cmdline attributes.
cmdline.history.maxsave = 10000
cmdline.clipboard.maxsave = 100

# Set the mode of mkdir and newfile in octal number.
mode.Mkdir.dirmode = 0o755
mode.Newfile.filemode = 0o644

# Set the prompt of shell mode.
mode.Shell.prompt = '$'

# Set message history.
message.Message.history = 100

# Set height of message box.
message.MessageBox.height = 4

# Set the default path of the directory creating.
Workspace.default_path = '~/'

# Set the workspace layout.
#
#     'Tile'
#     'TileLeft'
#     'TileTop'
#     'TileBottom'
#     'Oneline'
#     'Onecolumn'
#     'Magnifier'
#     'Fullscreen'
#
Workspace.layout = 'Tile'

# Set default kind of sorting in directory.
#
#     'Name[^]' -> Name sort of ascending order;
#     'Name[$]' -> Name sort of descending order;
#     'Size[^]' -> File size sort of ascending order;
#     'Size[$]' -> File size sort of descending order;
#     'Time[^]' -> Time sort of ascending order;
#     'Time[$]' -> Time sort of descending order;
#     'Permission[^]' -> Permission sort of ascending order;
#     'Permission[$]' -> Permission sort of descending order;
#     'Link[^]' -> Link sort of ascending order;
#     'Link[$]' -> Link sort of descending order;
#     'Ext[^]' -> File extension sort of ascending order;
#     'Ext[$]' -> File extension sort of descending order.
#
Directory.sort_kind = 'Name[^]'

# Set scroll type in directory.
#
#     'HalfScroll'
#     'PageScroll'
#     'ContinuousScroll'
#
Directory.scroll_type = 'HalfScroll'

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
FileStat.time_format = '%y-%m-%d %H:%M'

# Set the flag of file modified within 24 hours.
FileStat.time_24_flag = '!'
# Set the flag of file modified within a week.
FileStat.time_week_flag = '#'
# Set the flag of file modified more in old time.
FileStat.time_yore_flag = ' '

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

# Set borders.
# Smooth borders:
ui.StandardScreen.borders = []
ui.InfoBox.borders = []
# Classical borders:
# ui.StandardScreen.borders = ['|', '|', '-', '-', '+', '+', '+', '+']
# ui.InfoBox.borders = ['|', '|', '-', '-', '+', '+', '+', '+']

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
#
# The first argument of `atinit' is the function object
# called when initializing pyful.
# And the other arguments of `atinit' are a arguments of it.
#
# For example, add the following command when
# you load the history of `replace' in cmdline:
# >>> atinit(cmdline.history.loadfile, '~/.pyful/history/replace', 'Replace')
#
Pyful.atinit(filer.loadfile, '~/.pyful/info')
Pyful.atinit(cmdline.clipboard.loadfile, '~/.pyful/clipboard')
Pyful.atinit(cmdline.history.loadfile, '~/.pyful/history/shell', 'Shell')
Pyful.atinit(cmdline.history.loadfile, '~/.pyful/history/eval', 'Eval')
Pyful.atinit(cmdline.history.loadfile, '~/.pyful/history/replace', 'Replace')
Pyful.atinit(cmdline.history.loadfile, '~/.pyful/history/mx', 'Mx')

# Registration of program termination.
#
# The first argument and other arguments of `atexit' are similar to `atinit'
#
# For example, add the following command when
# you preserve the history of `replace' in cmdline:
# >>> atexit(cmdline.history.savefile, '~/.pyful/history/replace', 'Replace')
#
Pyful.atexit(filer.savefile, '~/.pyful/info')
Pyful.atexit(cmdline.clipboard.savefile, '~/.pyful/clipboard')
Pyful.atexit(cmdline.history.savefile, '~/.pyful/history/shell', 'Shell')
Pyful.atexit(cmdline.history.savefile, '~/.pyful/history/eval', 'Eval')
Pyful.atexit(cmdline.history.savefile, '~/.pyful/history/mx', 'Mx')
Pyful.atexit(cmdline.history.savefile, '~/.pyful/history/replace', 'Replace')

# Define the keymap of pyful.
#
# A key of the keymap dictionary is the tuple that consist of
# (meta, key) with the escape sequence and the keymap constant.
# A value of the keymap dictionary is the callable function of no argument.
#
# In the filer keymap, a key of the keymap dictionary is the tuple that
# consist of (meta, key) or (meta, key, ext).
# (meta, key, ext) tuple is consist of the escape sequence,
# the keymap constant and the file extension name.
#
# The following extension names are special:
#     '.dir' represent the directory;
#     '.link' represent the symbolic link;
#     '.exec' represent the executable file;
#     '.mark' represent the mark file.
#
# See keymap constants from pyful.keymap module.
#
myfilerkeymap = {
    (1, KEY_f        ): commands['view_next_workspace'],
    (1, KEY_b        ): commands['view_prev_workspace'],
    (1, KEY_F        ): commands['swap_workspace_inc'],
    (1, KEY_B        ): commands['swap_workspace_dec'],
    (1, KEY_1        ): lambda: filer.focus_workspace(0),
    (1, KEY_2        ): lambda: filer.focus_workspace(1),
    (1, KEY_3        ): lambda: filer.focus_workspace(2),
    (1, KEY_4        ): lambda: filer.focus_workspace(3),
    (1, KEY_5        ): lambda: filer.focus_workspace(4),
    (1, KEY_EXCLAM   ): lambda: filer.mvdir_workspace_to(0),
    (1, KEY_DQUOTE   ): lambda: filer.mvdir_workspace_to(1),
    (1, KEY_SHARP    ): lambda: filer.mvdir_workspace_to(2),
    (1, KEY_DOLLAR   ): lambda: filer.mvdir_workspace_to(3),
    (1, KEY_PERCENT  ): lambda: filer.mvdir_workspace_to(4),
    (0, KEY_CTRL_I   ): commands['focus_next_dir'],
    (0, KEY_CTRL_F   ): commands['focus_next_dir'],
    (0, KEY_CTRL_B   ): commands['focus_prev_dir'],
    (0, KEY_RIGHT    ): commands['focus_next_dir'],
    (0, KEY_LEFT     ): commands['focus_prev_dir'],
    (0, KEY_F        ): commands['swap_dir_inc'],
    (0, KEY_B        ): commands['swap_dir_dec'],
    (1, KEY_RETURN   ): commands['create_dir'],
    (1, KEY_C        ): commands['close_dir'],
    (0, KEY_CTRL_W   ): commands['close_dir'],
    (0, KEY_CTRL_L   ): commands['all_reload'],
    (0, KEY_CTRL_N   ): commands['filer_cursor_down'],
    (0, KEY_DOWN     ): commands['filer_cursor_down'],
    (0, KEY_CTRL_P   ): commands['filer_cursor_up'],
    (0, KEY_UP       ): commands['filer_cursor_up'],
    (0, KEY_CTRL_D   ): lambda: filer.dir.mvcursor(+5),
    (0, KEY_CTRL_U   ): lambda: filer.dir.mvcursor(-5),
    (0, KEY_CTRL_V   ): commands['filer_pagedown'],
    (0, KEY_NPAGE    ): commands['filer_pagedown'],
    (1, KEY_v        ): commands['filer_pageup'],
    (0, KEY_PPAGE    ): commands['filer_pageup'],
    (0, KEY_CTRL_A   ): commands['filer_settop'],
    (1, KEY_LSS      ): commands['filer_settop'],
    (0, KEY_CTRL_E   ): commands['filer_setbottom'],
    (1, KEY_GTR      ): commands['filer_setbottom'],
    (0, KEY_CTRL_G   ): commands['filer_reset'],
    (0, KEY_ESCAPE   ): commands['filer_reset'],
    (1, KEY_w        ): commands['switch_workspace'],
    (1, KEY_h        ): commands['chdir_backward'],
    (1, KEY_l        ): commands['chdir_forward'],
    (0, KEY_CTRL_H   ): commands['chdir_parent'],
    (0, KEY_BACKSPACE): commands['chdir_parent'],
    (0, KEY_TILDA    ): commands['chdir_home'],
    (0, KEY_BSLASH   ): commands['chdir_root'],
    (0, KEY_w        ): commands['chdir_neighbor'],
    (0, KEY_f        ): commands['finder_start'],
    (0, KEY_SLASH    ): commands['finder_start'],
    (0, KEY_v        ): commands['fileviewer'],
    (0, KEY_P        ): commands['pack'],
    (0, KEY_U        ): commands['unpack2'],
    (0, KEY_u        ): commands['unpack'],
    (0, KEY_END      ): commands['mark_toggle_all'],
    (0, KEY_SPACE    ): commands['mark_toggle'],
    (0, KEY_CTRL_R   ): commands['refresh_window'],
    (0, KEY_RETURN   ): commands['open_at_system'],
    (0, KEY_e        ): commands['spawn_editor'],
    (0, KEY_COLON    ): commands['spawn_shell'],
    (0, KEY_h        ): commands['shell'],
    (1, KEY_COLON    ): commands['eval'],
    (1, KEY_x        ): commands['mx'],
    (0, KEY_K        ): commands['kill_thread'],
    (0, KEY_QMARK    ): commands['help'],
    (1, KEY_QMARK    ): commands['help_all'],
    (0, KEY_c        ): commands['copy'],
    (0, KEY_DC       ): commands['delete'],
    (0, KEY_D        ): commands['delete'],
    (0, KEY_k        ): commands['mkdir'],
    (0, KEY_m        ): commands['move'],
    (0, KEY_n        ): commands['newfile'],
    (0, KEY_r        ): commands['rename'],
    (0, KEY_R        ): commands['replace'],
    (0, KEY_l        ): commands['symlink'],
    (0, KEY_d        ): commands['trashbox'],
    (0, KEY_t        ): commands['utime'],
    (0, KEY_x        ): commands['enter_exec'],
    (0, KEY_Q        ): commands['exit'],
    (0, KEY_RETURN, '.dir' ): commands['enter_dir'],
    (0, KEY_RETURN, '.mark'): commands['enter_mark'],
    (0, KEY_RETURN, '.link'): commands['enter_link'],
    (0, KEY_RETURN, '.exec'): commands['enter_exec'],
    (0, KEY_RETURN, '.tar'): commands['untar'],
    (0, KEY_RETURN, '.tgz'): commands['untar'],
    (0, KEY_RETURN, '.gz' ): commands['untar'],
    (0, KEY_RETURN, '.bz2'): commands['untar'],
    (0, KEY_RETURN, '.zip'): commands['unzip'],
    (0, KEY_RETURN, '.list'): commands['enter_listfile'],
    }

myfinderkeymap = {
    (1, KEY_n        ): lambda: filer.finder.history_select(-1),
    (1, KEY_p        ): lambda: filer.finder.history_select(+1),
    (0, KEY_CTRL_G   ): lambda: filer.finder.finish(),
    (0, KEY_ESCAPE   ): lambda: filer.finder.finish(),
    (0, KEY_CTRL_C   ): lambda: filer.finder.finish(),
    (0, KEY_CTRL_H   ): lambda: filer.finder.delete_backward_char(),
    (0, KEY_BACKSPACE): lambda: filer.finder.delete_backward_char(),
    }

mycmdlinekeymap = {
    (0, KEY_CTRL_F   ): lambda: cmdline.forward_char(),
    (0, KEY_RIGHT    ): lambda: cmdline.forward_char(),
    (0, KEY_CTRL_B   ): lambda: cmdline.backward_char(),
    (0, KEY_LEFT     ): lambda: cmdline.backward_char(),
    (1, KEY_f        ): lambda: cmdline.forward_word(),
    (1, KEY_b        ): lambda: cmdline.backward_word(),
    (0, KEY_CTRL_D   ): lambda: cmdline.delete_char(),
    (0, KEY_CTRL_H   ): lambda: cmdline.delete_backward_char(),
    (0, KEY_BACKSPACE): lambda: cmdline.delete_backward_char(),
    (1, KEY_d        ): lambda: cmdline.delete_forward_word(),
    (1, KEY_h        ): lambda: cmdline.delete_backward_word(),
    (0, KEY_CTRL_W   ): lambda: cmdline.delete_backward_word(),
    (0, KEY_CTRL_K   ): lambda: cmdline.kill_line(),
    (0, KEY_CTRL_U   ): lambda: cmdline.kill_line_all(),
    (0, KEY_CTRL_A   ): lambda: cmdline.settop(),
    (0, KEY_CTRL_E   ): lambda: cmdline.setbottom(),
    (0, KEY_CTRL_G   ): lambda: cmdline.escape(),
    (0, KEY_CTRL_C   ): lambda: cmdline.escape(),
    (0, KEY_ESCAPE   ): lambda: cmdline.escape(),
    (0, KEY_RETURN   ): lambda: cmdline.execute(),
    (1, KEY_m        ): lambda: cmdline.expandmacro(),
    (0, KEY_CTRL_Y   ): lambda: cmdline.clipboard.paste(),
    (1, KEY_y        ): lambda: cmdline.clipboard.start(),
    (0, KEY_CTRL_I   ): lambda: cmdline.completion.start(),
    (1, KEY_j        ): lambda: cmdline.output.infoarea(),
    (0, KEY_CTRL_N   ): lambda: cmdline.history.mvcursor(+1),
    (0, KEY_DOWN     ): lambda: cmdline.history.mvcursor(+1),
    (0, KEY_CTRL_P   ): lambda: cmdline.history.mvcursor(-1),
    (0, KEY_UP       ): lambda: cmdline.history.mvcursor(-1),
    (0, KEY_CTRL_V   ): lambda: cmdline.history.pagedown(),
    (1, KEY_v        ): lambda: cmdline.history.pageup(),
    (1, KEY_LSS      ): lambda: cmdline.history.settop(),
    (1, KEY_GTR      ): lambda: cmdline.history.setbottom(),
    (0, KEY_CTRL_X   ): lambda: cmdline.history.delete(),
    (1, KEY_PLUS     ): commands['zoom_in_infobox'],
    (1, KEY_MINUS    ): commands['zoom_out_infobox'],
    (1, KEY_EQUAL    ): commands['zoom_normal_infobox'],
    }

myclipboardkeymap = {
    (0, KEY_CTRL_N): lambda: cmdline.clipboard.mvcursor(1),
    (0, KEY_DOWN  ): lambda: cmdline.clipboard.mvcursor(1),
    (0, KEY_CTRL_V): lambda: cmdline.clipboard.pagedown(),
    (0, KEY_CTRL_D): lambda: cmdline.clipboard.pagedown(),
    (0, KEY_CTRL_P): lambda: cmdline.clipboard.mvcursor(-1),
    (0, KEY_UP    ): lambda: cmdline.clipboard.mvcursor(-1),
    (1, KEY_v     ): lambda: cmdline.clipboard.pageup(),
    (0, KEY_CTRL_U): lambda: cmdline.clipboard.pageup(),
    (0, KEY_CTRL_X): lambda: cmdline.clipboard.delete(),
    (0, KEY_CTRL_G): lambda: cmdline.clipboard.finish(),
    (0, KEY_CTRL_C): lambda: cmdline.clipboard.finish(),
    (0, KEY_ESCAPE): lambda: cmdline.clipboard.finish(),
    (0, KEY_RETURN): lambda: cmdline.clipboard.insert(),
    }

mycompletionkeymap = {
    (0, KEY_CTRL_N): lambda: cmdline.completion.cursordown(),
    (0, KEY_DOWN  ): lambda: cmdline.completion.cursordown(),
    (0, KEY_CTRL_P): lambda: cmdline.completion.cursorup(),
    (0, KEY_UP    ): lambda: cmdline.completion.cursorup(),
    (0, KEY_CTRL_I): lambda: cmdline.completion.mvcursor(+1),
    (0, KEY_CTRL_F): lambda: cmdline.completion.mvcursor(+1),
    (0, KEY_RIGHT ): lambda: cmdline.completion.mvcursor(+1),
    (0, KEY_CTRL_B): lambda: cmdline.completion.mvcursor(-1),
    (0, KEY_LEFT  ): lambda: cmdline.completion.mvcursor(-1),
    (0, KEY_CTRL_G): lambda: cmdline.completion.finish(),
    (0, KEY_CTRL_C): lambda: cmdline.completion.finish(),
    (0, KEY_ESCAPE): lambda: cmdline.completion.finish(),
    (0, KEY_RETURN): lambda: cmdline.completion.insert(),
    }

myoutputkeymap = {
    (0, KEY_CTRL_N): lambda: cmdline.output.mvcursor(1),
    (0, KEY_DOWN  ): lambda: cmdline.output.mvcursor(1),
    (0, KEY_CTRL_V): lambda: cmdline.output.pagedown(),
    (0, KEY_CTRL_D): lambda: cmdline.output.pagedown(),
    (0, KEY_CTRL_P): lambda: cmdline.output.mvcursor(-1),
    (0, KEY_UP    ): lambda: cmdline.output.mvcursor(-1),
    (1, KEY_v     ): lambda: cmdline.output.pageup(),
    (0, KEY_CTRL_U): lambda: cmdline.output.pageup(),
    (0, KEY_CTRL_G): lambda: cmdline.output.finish(),
    (0, KEY_CTRL_C): lambda: cmdline.output.finish(),
    (0, KEY_ESCAPE): lambda: cmdline.output.finish(),
    (0, KEY_RETURN): lambda: cmdline.output.edit(),
    }

mymenukeymap = {
    (0, KEY_CTRL_N): lambda: menu.mvcursor(+1),
    (0, KEY_DOWN  ): lambda: menu.mvcursor(+1),
    (0, KEY_CTRL_P): lambda: menu.mvcursor(-1),
    (0, KEY_UP    ): lambda: menu.mvcursor(-1),
    (0, KEY_CTRL_D): lambda: menu.mvcursor(+5),
    (0, KEY_CTRL_V): lambda: menu.mvcursor(+5),
    (0, KEY_CTRL_U): lambda: menu.mvcursor(-5),
    (1, KEY_v     ): lambda: menu.mvcursor(-5),
    (0, KEY_CTRL_G): lambda: menu.hide(),
    (0, KEY_CTRL_C): lambda: menu.hide(),
    (0, KEY_ESCAPE): lambda: menu.hide(),
    (0, KEY_RETURN): lambda: menu.run(),
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
#     - The second element is the keymap constant;
#     - The third element is the callable function of no argument.
#
menu.items['filer'] = (
    ('toggle (e)xtension' , KEY_e, commands['toggle_view_ext']),
    ('toggle (p)ermission', KEY_p, commands['toggle_view_permission']),
    ('toggle n(l)ink'     , KEY_l, commands['toggle_view_nlink']),
    ('toggle (u)ser'      , KEY_u, commands['toggle_view_user']),
    ('toggle (g)roup'     , KEY_g, commands['toggle_view_group']),
    ('toggle (s)ize'      , KEY_s, commands['toggle_view_size']),
    ('toggle m(t)ime'     , KEY_t, commands['toggle_view_mtime']),
    )

menu.items['layout'] = (
    ('(t)ile'        , KEY_t, commands['layout_tile']),
    ('tile(L)eft'    , KEY_L, commands['layout_tileleft']),
    ('tile(T)op'     , KEY_T, commands['layout_tiletop']),
    ('tile(B)ottom'  , KEY_B, commands['layout_tilebottom']),
    ('one(l)ine'     , KEY_l, commands['layout_oneline']),
    ('one(c)olumn'   , KEY_c, commands['layout_onecolumn']),
    ('(m)agnifier'   , KEY_m, commands['layout_magnifier']),
    ('(f)ullscreen'  , KEY_f, commands['layout_fullscreen']),
    )

menu.items['sort'] = (
    ('(n)ame'              , KEY_n, commands['sort_name']),
    ('(N)ame reverse'      , KEY_N, commands['sort_name_rev']),
    ('(e)xtension'         , KEY_e, commands['sort_ext']),
    ('(E)xtension reverse' , KEY_E, commands['sort_ext_rev']),
    ('(s)ize'              , KEY_s, commands['sort_size']),
    ('(S)ize reverse'      , KEY_S, commands['sort_size_rev']),
    ('(t)ime'              , KEY_t, commands['sort_time']),
    ('(T)ime reverse'      , KEY_T, commands['sort_time_rev']),
    ('(l)ink'              , KEY_l, commands['sort_nlink']),
    ('(L)ink reverse'      , KEY_L, commands['sort_nlink_rev']),
    ('(p)ermission'        , KEY_p, commands['sort_permission']),
    ('(P)ermission reverse', KEY_P, commands['sort_permission_rev']),
    )

menu.items["mark"] = (
    ("(r)egex mark", KEY_r, commands['mark']),
    ("(S)ource"    , KEY_S, commands['mark_source']),
    ("(A)rchive"   , KEY_A, commands['mark_archive']),
    ("(I)mage"     , KEY_I, commands['mark_image']),
    ("(M)usic"     , KEY_M, commands['mark_music']),
    ("(V)ideo"     , KEY_V, commands['mark_video']),
    ("mark (a)ll"  , KEY_a, commands['mark_all']),
    ("mark (c)lear", KEY_c, commands['mark_clear']),
    )

menu.items["mask"] = (
    ('(m)ask'   , KEY_m, commands['mask']),
    ('(S)ource' , KEY_S, commands['mask_source']),
    ('(A)rchive', KEY_A, commands['mask_archive']),
    ('(I)mage'  , KEY_I, commands['mask_image']),
    ('(M)usic'  , KEY_M, commands['mask_music']),
    ('(V)ideo'  , KEY_V, commands['mask_video']),
    ('(c)lear'  , KEY_c, commands['mask_clear']),
    )

# The editor launcher example.
menu.items["editor"] = (
    ("(e)macs"              , KEY_e, lambda: process.spawn("emacs -nw %f")),
    ("(E)macs new terminal" , KEY_E, lambda: process.spawn("emacs -nw %f %T")),
    ("emacs (f)rame"        , KEY_f, lambda: process.spawn("emacs %f")),
    ("(v)im"                , KEY_v, lambda: process.spawn("vim %f")),
    ("(V)im new terminal"   , KEY_V, lambda: process.spawn("vim %f %T")),
    ("(g)vim"               , KEY_g, lambda: process.spawn("gvim %f %&")),
    )

# The program launcher example.
menu.items['launcher'] = (
    ('(h)top'           , KEY_h, lambda: process.spawn('htop %T')),
    ('(m)c'             , KEY_m, lambda: process.spawn('mc %T')),
    ('(M)OC'            , KEY_M, lambda: process.spawn('mocp %T')),
    ('(w)3m'            , KEY_w, lambda: process.spawn('w3m google.com %T')),
    ('(f)irefox'        , KEY_f, lambda: process.spawn('firefox %&')),
    ('(T)hunderbird'    , KEY_T, lambda: process.spawn('thunderbird %&')),
    ('(a)marok'         , KEY_a, lambda: process.spawn('amarok %&')),
    ('(g)imp'           , KEY_g, lambda: process.spawn('gimp %&')),
    ('(t)erminator'     , KEY_t, lambda: process.spawn('terminator %&')),
    ('(n)autilus'       , KEY_n, lambda: process.spawn('nautilus --no-desktop %D %&')),
    ('(s)ystem-monitor' , KEY_s, lambda: process.spawn('gnome-system-monitor %&')),
    ('(S)ynaptic'       , KEY_S, lambda: process.spawn('gksu synaptic %&')),
    )

# Update the filer keymap.
filer.keymap.update({
        (0 , KEY_V     ): lambda: menu.show('filer'),
        (0 , KEY_s     ): lambda: menu.show('sort'),
        (0 , KEY_L     ): lambda: menu.show('layout'),
        (0 , KEY_STAR  ): lambda: menu.show('mark'),
        (0 , KEY_PLUS  ): lambda: menu.show('mask'),
        (0 , KEY_E     ): lambda: menu.show('editor'),
        (0 , KEY_SCOLON): lambda: menu.show('launcher'),
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
menu.items['image'] = (
    ('(d)isplay'    , KEY_d, lambda: process.spawn('display %f %&')),
    ('(g)imp'       , KEY_g, lambda: process.spawn('gimp %f %&')),
    )

# Define a music file associate the menu item.
menu.items['music'] = (
    ('(m)player'  , KEY_m, lambda: process.spawn('mplayer %m')),
    ('(M)OC'      , KEY_M, lambda: process.spawn('mocp -a %m %&')),
    ('(a)marok'   , KEY_a, lambda: process.spawn('amarok %f %&')),
    )

# Define a video file associate the menu item.
menu.items['video'] = (
    ('(m)player'  , KEY_m, lambda: process.spawn('mplayer %f')),
    ('(v)lc'      , KEY_v, lambda: process.spawn('vlc %f %&')),
    )

myassociation = {
    (0 , KEY_RETURN , '.py'   ): lambda: cmdline.shell('python %f'),
    (0 , KEY_RETURN , '.rb'   ): lambda: cmdline.shell('ruby %f'),
    (0 , KEY_RETURN , '.sh'   ): lambda: cmdline.shell('sh %f'),
    (0 , KEY_RETURN , '.exe'  ): lambda: cmdline.shell('wine %f'),
    (0 , KEY_RETURN , '.c'    ): lambda: cmdline.shell('gcc %f'),
    (0 , KEY_RETURN , '.java' ): lambda: cmdline.shell('javac %f'),
    (0 , KEY_RETURN , '.class'): lambda: cmdline.shell('java %x'),
    (0 , KEY_RETURN , '.jar'  ): lambda: cmdline.shell('java -jar %f'),
    (0 , KEY_RETURN , '.jpg'  ): lambda: menu.show('image'),
    (0 , KEY_RETURN , '.gif'  ): lambda: menu.show('image'),
    (0 , KEY_RETURN , '.png'  ): lambda: menu.show('image'),
    (0 , KEY_RETURN , '.bmp'  ): lambda: menu.show('image'),
    (0 , KEY_RETURN , '.mp3'  ): lambda: menu.show('music'),
    (0 , KEY_RETURN , '.flac' ): lambda: menu.show('music'),
    (0 , KEY_RETURN , '.avi'  ): lambda: menu.show('video'),
    (0 , KEY_RETURN , '.mp4'  ): lambda: menu.show('video'),
    (0 , KEY_RETURN , '.flv'  ): lambda: menu.show('video'),
    }

filer.keymap.update(myassociation)

import os, sys
if'screen' in os.getenv("TERM"):
    # Change GNU SCREEN's title.
    sys.stdout.write('\033kpyful\033\\')
else:
    # Change terminal emulator's title.
    import socket
    sys.stdout.write('\033]0;pyful@{0}\007'.format(socket.gethostname()))

