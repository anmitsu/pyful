# coding: utf-8
#
# pyful configure file.
# This file is executed in the local namespace and not generate module.
#

from pyfulib.core import Pyful
from pyfulib.command import commands
from pyfulib.filer import Workspace, Directory, Finder, FileStat
from pyfulib import mode
from pyfulib import process
from pyfulib.keymap import *

# Get PYthon File management UtiLity.
pyful = Pyful()

# Set environments of pyful.
pyful.environs['EDITOR'] = 'vim'
pyful.environs['PAGER'] = 'less'
pyful.environs['TRASHBOX'] = '~/.pyful/trashbox'

# Set proc attributes.
process.Process.shell = ('/bin/bash', '-c')
process.Process.terminal_emulator = ('x-terminal-emulator', '-e')

# Set cmdline attributes.
pyful.cmdline.history.maxsave = 10000
pyful.cmdline.clipboard.maxsave = 100

# Set the mode of mkdir and newfile in octal number.
mode.Mkdir.dirmode = 0o755
mode.Newfile.filemode = 0o644

# Set the prompt of shell mode.
mode.Shell.prompt = '$'

# Set the default path of the directory creating.
Workspace.default_path = '~/'

# Set the workspace layout.
#
# The workspace layout indicate as follows:
#     'Tile'
#     'Tile reverse'
#     'Oneline'
#     'Onecolumn'
#     'Fullscreen'
#
Workspace.layout = 'Tile'

# Set default kind of sorting in directory.
#
# The kind of sorting indicate as follows:
#     Name[^] -> Name sort of ascending order;
#     Name[$] -> Name sort of descending order;
#     Size[^] -> File size sort of ascending order;
#     Size[$] -> File size sort of descending order;
#     Time[^] -> Time sort of ascending order;
#     Time[$] -> Time sort of descending order;
#     Permission[^] -> Permission sort of ascending order;
#     Permission[$] -> Permission sort of descending order;
#     Link[^] -> Link sort of ascending order;
#     Link[$] -> Link sort of descending order;
#     Ext[^] -> File extension sort of ascending order;
#     Ext[$] -> File extension sort of descending order.
#
Directory.sort_kind = 'Name[^]'

# Distinguish upper case and lower case at a finder?
Finder.smartcase = True

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
FileStat.view_ext = True
# Display the file permission?
FileStat.view_permission = True
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

# Registration of program initialization.
#
# The first argument of `atinit' is the function object
# called when initializing pyful.
# And the other arguments of `atinit' are a arguments of it.
#
# For example, add the following command when
# you load the history of `replace' in cmdline:
# >>> pyful.atinit(pyful.cmdline.history.loadfile, '~/.pyful/history/replace', 'Replace')
#
pyful.atinit(pyful.filer.loadfile, '~/.pyful/info')
pyful.atinit(pyful.cmdline.clipboard.loadfile, '~/.pyful/clipboard')
pyful.atinit(pyful.cmdline.history.loadfile, '~/.pyful/history/shell', 'Shell')
pyful.atinit(pyful.cmdline.history.loadfile, '~/.pyful/history/eval', 'Eval')
pyful.atinit(pyful.cmdline.history.loadfile, '~/.pyful/history/mx', 'Mx')

# Registration of program termination.
#
# The first argument and other arguments of `atexit' are similar to `atinit'
#
# For example, add the following command when
# you preserve the history of `replace' in cmdline:
# >>> pyful.atexit(pyful.cmdline.history.savefile, '~/.pyful/history/replace', 'Replace')
#
pyful.atexit(pyful.filer.savefile, '~/.pyful/info')
pyful.atexit(pyful.cmdline.clipboard.savefile, '~/.pyful/clipboard')
pyful.atexit(pyful.cmdline.history.savefile, '~/.pyful/history/shell', 'Shell')
pyful.atexit(pyful.cmdline.history.savefile, '~/.pyful/history/eval', 'Eval')
pyful.atexit(pyful.cmdline.history.savefile, '~/.pyful/history/mx', 'Mx')

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
# See keymap constants from pyfulib.keymap module.
#
myfilerkeymap = {
    (1, KEY_f        ): lambda: pyful.filer.next_workspace(),
    (1, KEY_b        ): lambda: pyful.filer.prev_workspace(),
    (1, KEY_1        ): lambda: pyful.filer.focus_workspace(0),
    (1, KEY_2        ): lambda: pyful.filer.focus_workspace(1),
    (1, KEY_3        ): lambda: pyful.filer.focus_workspace(2),
    (1, KEY_4        ): lambda: pyful.filer.focus_workspace(3),
    (1, KEY_5        ): lambda: pyful.filer.focus_workspace(4),
    (1, KEY_F        ): lambda: pyful.filer.swap_workspace_inc(),
    (1, KEY_B        ): lambda: pyful.filer.swap_workspace_dec(),
    (1, KEY_EXCLAM   ): lambda: pyful.filer.mvdir_workspace_to(0),
    (1, KEY_DQUOTE   ): lambda: pyful.filer.mvdir_workspace_to(1),
    (1, KEY_SHARP    ): lambda: pyful.filer.mvdir_workspace_to(2),
    (1, KEY_DOLLAR   ): lambda: pyful.filer.mvdir_workspace_to(3),
    (1, KEY_PERCENT  ): lambda: pyful.filer.mvdir_workspace_to(4),
    (0, KEY_CTRL_I   ): lambda: pyful.filer.workspace.mvcursor(+1),
    (0, KEY_CTRL_F   ): lambda: pyful.filer.workspace.mvcursor(+1),
    (0, KEY_CTRL_B   ): lambda: pyful.filer.workspace.mvcursor(-1),
    (0, KEY_RIGHT    ): lambda: pyful.filer.workspace.mvcursor(+1),
    (0, KEY_LEFT     ): lambda: pyful.filer.workspace.mvcursor(-1),
    (0, KEY_F        ): lambda: pyful.filer.workspace.swap_dir_inc(),
    (0, KEY_B        ): lambda: pyful.filer.workspace.swap_dir_dec(),
    (1, KEY_RETURN   ): lambda: pyful.filer.workspace.create_dir(),
    (1, KEY_C        ): lambda: pyful.filer.workspace.close_dir(),
    (0, KEY_CTRL_W   ): lambda: pyful.filer.workspace.close_dir(),
    (0, KEY_CTRL_L   ): lambda: pyful.filer.workspace.all_reload(),
    (0, KEY_CTRL_N   ): lambda: pyful.filer.dir.mvcursor(+1),
    (0, KEY_DOWN     ): lambda: pyful.filer.dir.mvcursor(+1),
    (0, KEY_CTRL_P   ): lambda: pyful.filer.dir.mvcursor(-1),
    (0, KEY_UP       ): lambda: pyful.filer.dir.mvcursor(-1),
    (0, KEY_CTRL_D   ): lambda: pyful.filer.dir.mvcursor(+5),
    (0, KEY_CTRL_U   ): lambda: pyful.filer.dir.mvcursor(-5),
    (0, KEY_CTRL_V   ): lambda: pyful.filer.dir.pagedown(),
    (1, KEY_v        ): lambda: pyful.filer.dir.pageup(),
    (0, KEY_CTRL_A   ): lambda: pyful.filer.dir.settop(),
    (1, KEY_LSS      ): lambda: pyful.filer.dir.settop(),
    (0, KEY_CTRL_E   ): lambda: pyful.filer.dir.setbottom(),
    (1, KEY_GTR      ): lambda: pyful.filer.dir.setbottom(),
    (0, KEY_CTRL_G   ): lambda: pyful.filer.dir.reset(),
    (0, KEY_ESCAPE   ): lambda: pyful.filer.dir.reset(),
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
    (0, KEY_c        ): commands['copy'],
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
    (1, KEY_n        ): lambda: pyful.filer.finder.history_select(-1),
    (1, KEY_p        ): lambda: pyful.filer.finder.history_select(+1),
    (0, KEY_CTRL_G   ): lambda: pyful.filer.finder.finish(),
    (0, KEY_ESCAPE   ): lambda: pyful.filer.finder.finish(),
    (0, KEY_CTRL_C   ): lambda: pyful.filer.finder.finish(),
    (0, KEY_CTRL_H   ): lambda: pyful.filer.finder.delete_backward_char(),
    (0, KEY_BACKSPACE): lambda: pyful.filer.finder.delete_backward_char(),
    }

mycmdlinekeymap = {
    (0, KEY_CTRL_F   ): lambda: pyful.cmdline.forward_char(),
    (0, KEY_RIGHT    ): lambda: pyful.cmdline.forward_char(),
    (0, KEY_CTRL_B   ): lambda: pyful.cmdline.backward_char(),
    (0, KEY_LEFT     ): lambda: pyful.cmdline.backward_char(),
    (1, KEY_f        ): lambda: pyful.cmdline.forward_word(),
    (1, KEY_b        ): lambda: pyful.cmdline.backward_word(),
    (0, KEY_CTRL_D   ): lambda: pyful.cmdline.delete_char(),
    (0, KEY_CTRL_H   ): lambda: pyful.cmdline.delete_backward_char(),
    (0, KEY_BACKSPACE): lambda: pyful.cmdline.delete_backward_char(),
    (1, KEY_d        ): lambda: pyful.cmdline.delete_forward_word(),
    (1, KEY_h        ): lambda: pyful.cmdline.delete_backward_word(),
    (0, KEY_CTRL_W   ): lambda: pyful.cmdline.delete_backward_word(),
    (0, KEY_CTRL_K   ): lambda: pyful.cmdline.kill_line(),
    (0, KEY_CTRL_U   ): lambda: pyful.cmdline.kill_line_all(),
    (0, KEY_CTRL_A   ): lambda: pyful.cmdline.settop(),
    (0, KEY_CTRL_E   ): lambda: pyful.cmdline.setbottom(),
    (0, KEY_CTRL_G   ): lambda: pyful.cmdline.escape(),
    (0, KEY_CTRL_C   ): lambda: pyful.cmdline.escape(),
    (0, KEY_ESCAPE   ): lambda: pyful.cmdline.escape(),
    (0, KEY_RETURN   ): lambda: pyful.cmdline.execute(),
    (1, KEY_m        ): lambda: pyful.cmdline.expandmacro(),
    (0, KEY_CTRL_Y   ): lambda: pyful.cmdline.clipboard.paste(),
    (1, KEY_y        ): lambda: pyful.cmdline.clipboard.start(),
    (0, KEY_CTRL_I   ): lambda: pyful.cmdline.completion.start(),
    (1, KEY_j        ): lambda: pyful.cmdline.output.infoarea(),
    (0, KEY_CTRL_N   ): lambda: pyful.cmdline.history.mvcursor(+1),
    (0, KEY_DOWN     ): lambda: pyful.cmdline.history.mvcursor(+1),
    (0, KEY_CTRL_P   ): lambda: pyful.cmdline.history.mvcursor(-1),
    (0, KEY_UP       ): lambda: pyful.cmdline.history.mvcursor(-1),
    (0, KEY_CTRL_V   ): lambda: pyful.cmdline.history.pagedown(),
    (1, KEY_v        ): lambda: pyful.cmdline.history.pageup(),
    (1, KEY_LSS      ): lambda: pyful.cmdline.history.settop(),
    (1, KEY_GTR      ): lambda: pyful.cmdline.history.setbottom(),
    (0, KEY_CTRL_X   ): lambda: pyful.cmdline.history.delete(),
    }

myclipboardkeymap = {
    (0, KEY_CTRL_N): lambda: pyful.cmdline.clipboard.mvcursor(1),
    (0, KEY_DOWN  ): lambda: pyful.cmdline.clipboard.mvcursor(1),
    (0, KEY_CTRL_V): lambda: pyful.cmdline.clipboard.pagedown(),
    (0, KEY_CTRL_D): lambda: pyful.cmdline.clipboard.pagedown(),
    (0, KEY_CTRL_P): lambda: pyful.cmdline.clipboard.mvcursor(-1),
    (0, KEY_UP    ): lambda: pyful.cmdline.clipboard.mvcursor(-1),
    (1, KEY_v     ): lambda: pyful.cmdline.clipboard.pageup(),
    (0, KEY_CTRL_U): lambda: pyful.cmdline.clipboard.pageup(),
    (0, KEY_CTRL_X): lambda: pyful.cmdline.clipboard.delete(),
    (0, KEY_CTRL_G): lambda: pyful.cmdline.clipboard.finish(),
    (0, KEY_CTRL_C): lambda: pyful.cmdline.clipboard.finish(),
    (0, KEY_ESCAPE): lambda: pyful.cmdline.clipboard.finish(),
    (0, KEY_RETURN): lambda: pyful.cmdline.clipboard.insert(),
    }

mycompletionkeymap = {
    (0, KEY_CTRL_N): lambda: pyful.cmdline.completion.mvcursor(+pyful.cmdline.completion.maxrow),
    (0, KEY_DOWN  ): lambda: pyful.cmdline.completion.mvcursor(+pyful.cmdline.completion.maxrow),
    (0, KEY_CTRL_P): lambda: pyful.cmdline.completion.mvcursor(-pyful.cmdline.completion.maxrow),
    (0, KEY_UP    ): lambda: pyful.cmdline.completion.mvcursor(-pyful.cmdline.completion.maxrow),
    (0, KEY_CTRL_I): lambda: pyful.cmdline.completion.mvcursor(+1),
    (0, KEY_CTRL_F): lambda: pyful.cmdline.completion.mvcursor(+1),
    (0, KEY_RIGHT ): lambda: pyful.cmdline.completion.mvcursor(+1),
    (0, KEY_CTRL_B): lambda: pyful.cmdline.completion.mvcursor(-1),
    (0, KEY_LEFT  ): lambda: pyful.cmdline.completion.mvcursor(-1),
    (0, KEY_CTRL_G): lambda: pyful.cmdline.completion.finish(),
    (0, KEY_CTRL_C): lambda: pyful.cmdline.completion.finish(),
    (0, KEY_ESCAPE): lambda: pyful.cmdline.completion.finish(),
    (0, KEY_RETURN): lambda: pyful.cmdline.completion.insert(),
    }

myoutputkeymap = {
    (0, KEY_CTRL_N): lambda: pyful.cmdline.output.mvcursor(1),
    (0, KEY_DOWN  ): lambda: pyful.cmdline.output.mvcursor(1),
    (0, KEY_CTRL_V): lambda: pyful.cmdline.output.pagedown(),
    (0, KEY_CTRL_D): lambda: pyful.cmdline.output.pagedown(),
    (0, KEY_CTRL_P): lambda: pyful.cmdline.output.mvcursor(-1),
    (0, KEY_UP    ): lambda: pyful.cmdline.output.mvcursor(-1),
    (1, KEY_v     ): lambda: pyful.cmdline.output.pageup(),
    (0, KEY_CTRL_U): lambda: pyful.cmdline.output.pageup(),
    (0, KEY_CTRL_G): lambda: pyful.cmdline.output.finish(),
    (0, KEY_CTRL_C): lambda: pyful.cmdline.output.finish(),
    (0, KEY_ESCAPE): lambda: pyful.cmdline.output.finish(),
    (0, KEY_RETURN): lambda: pyful.cmdline.output.edit(),
    }

mymenukeymap = {
    (0, KEY_CTRL_N): lambda: pyful.menu.mvcursor(+1),
    (0, KEY_DOWN  ): lambda: pyful.menu.mvcursor(+1),
    (0, KEY_CTRL_P): lambda: pyful.menu.mvcursor(-1),
    (0, KEY_UP    ): lambda: pyful.menu.mvcursor(-1),
    (0, KEY_CTRL_D): lambda: pyful.menu.mvcursor(+5),
    (0, KEY_CTRL_V): lambda: pyful.menu.mvcursor(+5),
    (0, KEY_CTRL_U): lambda: pyful.menu.mvcursor(-5),
    (1, KEY_v     ): lambda: pyful.menu.mvcursor(-5),
    (0, KEY_CTRL_G): lambda: pyful.menu.hide(),
    (0, KEY_CTRL_C): lambda: pyful.menu.hide(),
    (0, KEY_ESCAPE): lambda: pyful.menu.hide(),
    (0, KEY_RETURN): lambda: pyful.menu.run(),
    }

# Update the keymap of pyful.
pyful.filer.keymap.update(myfilerkeymap)
pyful.filer.finder.keymap.update(myfinderkeymap)
pyful.cmdline.keymap.update(mycmdlinekeymap)
pyful.cmdline.keymap.update(mycmdlinekeymap)
pyful.cmdline.clipboard.keymap.update(myclipboardkeymap)
pyful.cmdline.completion.keymap.update(mycompletionkeymap)
pyful.cmdline.output.keymap.update(myoutputkeymap)
pyful.menu.keymap.update(mymenukeymap)

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
pyful.menu.items['filer'] = (
    ('toggle (e)xtension' , KEY_e, commands['toggle_view_ext']),
    ('toggle (p)ermission', KEY_p, commands['toggle_view_permission']),
    ('toggle n(l)ink'     , KEY_l, commands['toggle_view_nlink']),
    ('toggle (u)ser'      , KEY_u, commands['toggle_view_user']),
    ('toggle (g)roup'     , KEY_g, commands['toggle_view_group']),
    ('toggle (s)ize'      , KEY_s, commands['toggle_view_size']),
    ('toggle m(t)ime'     , KEY_t, commands['toggle_view_mtime']),
    )

pyful.menu.items['layout'] = (
    ('(t)ile'        , KEY_t, commands['layout_tile']),
    ('(T)ile reverse', KEY_T, commands['layout_tile_rev']),
    ('one(l)ine'     , KEY_l, commands['layout_oneline']),
    ('one(c)olumn'   , KEY_c, commands['layout_onecolumn']),
    ('(f)ullscreen'  , KEY_f, commands['layout_fullscreen']),
    )

pyful.menu.items['sort'] = (
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

pyful.menu.items["mark"] = (
    ("(r)egex mark", KEY_r, commands['mark']),
    ("(S)ource"    , KEY_S, commands['mark_source']),
    ("(A)rchive"   , KEY_A, commands['mark_archive']),
    ("(I)mage"     , KEY_I, commands['mark_image']),
    ("(M)usic"     , KEY_M, commands['mark_music']),
    ("(V)ideo"     , KEY_V, commands['mark_video']),
    ("mark (a)ll"  , KEY_a, commands['mark_all']),
    ("mark (c)lear", KEY_c, commands['mark_clear']),
    )

pyful.menu.items["mask"] = (
    ('(m)ask'   , KEY_m, commands['mask']),
    ('(S)ource' , KEY_S, commands['mask_source']),
    ('(A)rchive', KEY_A, commands['mask_archive']),
    ('(I)mage'  , KEY_I, commands['mask_image']),
    ('(M)usic'  , KEY_M, commands['mask_music']),
    ('(V)ideo'  , KEY_V, commands['mask_video']),
    ('(c)lear'  , KEY_c, commands['mask_clear']),
    )

# The editor launcher example.
pyful.menu.items["editor"] = (
    ("(e)macs"              , KEY_e, lambda: process.spawn("emacs -nw %f")),
    ("(E)macs new terminal" , KEY_E, lambda: process.spawn("emacs -nw %f %T")),
    ("emacs (f)rame"        , KEY_f, lambda: process.spawn("emacs %f")),
    ("(v)im"                , KEY_v, lambda: process.spawn("vim %f")),
    ("(V)im new terminal"   , KEY_V, lambda: process.spawn("vim %f %T")),
    ("(g)vim"               , KEY_g, lambda: process.spawn("gvim %f %&")),
    )

# The program launcher example.
pyful.menu.items['launcher'] = (
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
pyful.filer.keymap.update({
        (0 , KEY_V     ): lambda: pyful.menu.show('filer'),
        (0 , KEY_s     ): lambda: pyful.menu.show('sort'),
        (0 , KEY_L     ): lambda: pyful.menu.show('layout'),
        (0 , KEY_STAR  ): lambda: pyful.menu.show('mark'),
        (0 , KEY_PLUS  ): lambda: pyful.menu.show('mask'),
        (0 , KEY_E     ): lambda: pyful.menu.show('editor'),
        (0 , KEY_SCOLON): lambda: pyful.menu.show('launcher'),
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
pyful.menu.items['image'] = (
    ('(d)isplay'    , KEY_d, lambda: process.spawn('display %f %&')),
    ('(g)imp'       , KEY_g, lambda: process.spawn('gimp %f %&')),
    )

# Define a music file associate the menu item.
pyful.menu.items['music'] = (
    ('(m)player'  , KEY_m, lambda: process.spawn('mplayer %m')),
    ('(M)OC'      , KEY_M, lambda: process.spawn('mocp -a %m %&')),
    ('(a)marok'   , KEY_a, lambda: process.spawn('amarok %f %&')),
    )

# Define a video file associate the menu item.
pyful.menu.items['video'] = (
    ('(m)player'  , KEY_m, lambda: process.spawn('mplayer %f')),
    ('(v)lc'      , KEY_v, lambda: process.spawn('vlc %f %&')),
    )

myassociation = {
    (0 , KEY_RETURN , '.py'   ): lambda: pyful.cmdline.shell('python %f'),
    (0 , KEY_RETURN , '.rb'   ): lambda: pyful.cmdline.shell('ruby %f'),
    (0 , KEY_RETURN , '.sh'   ): lambda: pyful.cmdline.shell('sh %f'),
    (0 , KEY_RETURN , '.exe'  ): lambda: pyful.cmdline.shell('wine %f'),
    (0 , KEY_RETURN , '.c'    ): lambda: pyful.cmdline.shell('gcc %f'),
    (0 , KEY_RETURN , '.java' ): lambda: pyful.cmdline.shell('javac %f'),
    (0 , KEY_RETURN , '.class'): lambda: pyful.cmdline.shell('java %x'),
    (0 , KEY_RETURN , '.jar'  ): lambda: pyful.cmdline.shell('java -jar %f'),
    (0 , KEY_RETURN , '.jpg'  ): lambda: pyful.menu.show('image'),
    (0 , KEY_RETURN , '.gif'  ): lambda: pyful.menu.show('image'),
    (0 , KEY_RETURN , '.png'  ): lambda: pyful.menu.show('image'),
    (0 , KEY_RETURN , '.bmp'  ): lambda: pyful.menu.show('image'),
    (0 , KEY_RETURN , '.mp3'  ): lambda: pyful.menu.show('music'),
    (0 , KEY_RETURN , '.flac' ): lambda: pyful.menu.show('music'),
    (0 , KEY_RETURN , '.avi'  ): lambda: pyful.menu.show('video'),
    (0 , KEY_RETURN , '.mp4'  ): lambda: pyful.menu.show('video'),
    (0 , KEY_RETURN , '.flv'  ): lambda: pyful.menu.show('video'),
    }

pyful.filer.keymap.update(myassociation)

if not pyful.started:
    import os
    if'screen' in os.environ['TERM']:
        # Change GNU SCREEN's title.
        print('\033kpyful\033\\')
    else:
        # Change terminal emulator's title.
        import socket
        print('\033]0;pyful@%s\007' % socket.gethostname())

