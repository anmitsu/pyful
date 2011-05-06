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

from pyful import completion
from pyful.completion import Argument

def _screen_arguments(f): return (
    ("-a"             , "-- force all capabilities into each window's termcap", f.default),
    ("-A"             , "-- adapt all windows to the new display width & height", f.default),
    ("-c"             , "-- read configuration file instead of '.screenrc'", f.comp_files),
    ("-d"             , "-- detach the elsewhere running screen (with -r: reattach here)", f.default),
    ("-dmS"           , "-- start as daemon, screen session in detached mode", []),
    ("-D"             , "-- detach and logout remote (with -r: reattach here)", []),
    ("-e"             , "-- change command characters", []),
    ("-f"             , "-- set flow control", f.default),
    ("-h"             , "-- set the size of the scrollback history buffer", []),
    ("-i"             , "-- interrupt output sooner when flow control is on", f.default),
    ("-l"             , "-- login mode on (update utmp database)", f.default),
    (("-list", "-ls") , "-- list sessions/socket directory", f.default),
    ("-L"             , "-- terminal's last character can be safely updated", f.default),
    ("-m"             , "-- ignore $STY variable, do create a new screen session", f.default),
    ("-O"             , "-- choose optimal output rather than exact vt100 emulation", f.default),
    ("-p"             , "-- preselect the named window", []),
    ("-q"             , "-- quiet startup, exit with non-zero return code if unsuccessful", f.default),
    ("-r"             , "-- reattach to a detached screen process", []),
    ("-R"             , "-- reattach if possible, otherwise start a new session", []),
    ("-s"             , "-- shell to execute rather than $SHELL", f.default),
    ("-S"             , "-- name this session <pid>.sockname instead of <pid>.<tty>.<host>", []),
    ("-t"             , "-- set title (window's name)", []),
    ("-T"             , "-- use term as $TERM for windows, rather than \"screen\"", []),
    ("-U"             , "-- tell screen to use UTF-8 encoding", f.default),
    ("-v"             , "-- print screen version", f.default),
    ("-wipe"          , "-- do nothing, clean up SockDir", f.default),
    ("-x"             , "-- attach to a not detached screen (multi display mode)", []),
    ("-X"             , "-- execute command as a screen command in the specified session", _screen_commands),
    )

def _screen_commands(): return (
    "acladd",            "aclchg",            "acldel",            "aclgrp",
    "aclumask",          "activity",          "addacl",            "allpartial",
    "altscreen",         "at",                "attrcolor",         "autodetach",
    "autonuke",          "backtick",          "bce",               "bd_bc_down",
    "bd_bc_left",        "bd_bc_right",       "bd_bc_up",          "bd_bell",
    "bd_braille_table",  "bd_eightdot",       "bd_info",           "bd_link",
    "bd_lower_left",     "bd_lower_right",    "bd_ncrc",           "bd_port",
    "bd_scroll",         "bd_skip",           "bd_start_braille",  "bd_type",
    "bd_upper_left",     "bd_upper_right",    "bd_width",          "bell_msg",
    "bind",              "bindkey",           "blanker",           "blankerprg",
    "break",             "breaktype",         "bufferfile",        "c1",
    "caption",           "chacl",             "charset",           "chdir",
    "clear",             "colon",             "command",           "compacthist",
    "console",           "copy",              "crlf",              "debug",
    "defautonuke",       "defbce",            "defbreaktype",      "defc1",
    "defcharset",        "defencoding",       "defescape",         "defflow",
    "defgr",             "defhstatus",        "defkanji",          "deflog",
    "deflogin",          "defmode",           "defmonitor",        "defnonblock",
    "defobuflimit",      "defscrollback",     "defshell",          "defsilence",
    "defslowpaste",      "defutf8",           "defwrap",           "defwritelock",
    "detach",            "digraph",           "dinfo",             "displays",
    "dumptermcap",       "echo",              "encoding",          "escape",
    "eval",              "exec",              "fit",               "flow",
    "focus",             "gr",                "hardcopy",          "hardcopy_append",
    "hardcopydir",       "hardstatus",        "height",            "help",
    "history",           "hstatus",           "idle",              "ignorecase",
    "info",              "kanji",             "kill",              "lastmsg",
    "license",           "lockscreen",        "log",               "logfile",
    "login",             "logtstamp",         "mapdefault",        "mapnotnext",
    "maptimeout",        "markkeys",          "maxwin",            "meta",
    "monitor",           "msgminwait",        "msgwait",           "multiuser",
    "nethack",           "next",              "nonblock",          "number",
    "obuflimit",         "only",              "other",             "partial",
    "password",          "paste",             "pastefont",         "pow_break",
    "pow_detach",        "pow_detach_msg",    "prev",              "printcmd",
    "process",           "quit",              "readbuf",           "readreg",
    "redisplay",         "register",          "remove",            "removebuf",
    "reset",             "resize",            "screen",            "scrollback",
    "select",            "sessionname",       "setenv",            "setsid",
    "shell",             "shelltitle",        "silence",           "silencewait",
    "sleep",             "slowpaste",         "sorendition",       "source",
    "split",             "startup_message",   "stuff",             "su",
    "suspend",           "term",              "termcap",           "termcapinfo",
    "terminfo",          "time",              "title",             "umask",
    "unsetenv",          "utf8",              "vbell",             "vbell_msg",
    "vbellwait",         "verbose",           "version",           "wall",
    "width",             "windowlist",        "windows",           "wrap",
    "writebuf",          "writelock",         "xoff",              "xon",
    "zmodem",            "zombie",
    )

class Screen(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _screen_arguments(self)]

    def default(self):
        return self.comp_programs()

completion.register("screen", Screen)
completion.register("byobu", Screen)
