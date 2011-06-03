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
import subprocess

from pyful import completion
from pyful.completion import Argument

def _ruby_arguments(f): return (
    ("-0"                , "-- specify record separator", f.comp_files),
    ("-C"                , "-- cd to directory, before executing your script", f.comp_files),
    ("-F"                , "-- split() pattern for autosplit (-a)", f.comp_files),
    ("-I"                , "-- specify $LOAD_PATH directory (may be used more than once)", f.comp_files),
    ("-K"                , "-- specifies KANJI (Japanese) code-set", f.comp_files),
    ("-S"                , "-- look for the script using PATH environment variable", f.comp_files),
    ("-T"                , "-- turn on tainting checks", f.comp_files),
    ("-W"                , "-- set warning level", f.comp_files),
    ("-a"                , "-- autosplit mode with -n or -p (splits $_ into $F)", f.comp_files),
    ("-c"                , "-- check syntax only", f.comp_files),
    ("-e"                , "-- one line of script (several -e's allowed, omit program file)", []),
    ("-i"                , "-- edit ARGV files in place (make backup if extension supplied)", f.comp_files),
    (("-n", "-l")        , "-- assume 'while gets(); ... end' loop around your script", f.comp_files),
    ("-p"                , "-- assume loop like -n but print line also like sed", f.comp_files),
    ("-r"                , "-- require the library, before executing your script", _ruby_library),
    ("-s"                , "-- enable some switch parsing for switches after script name", f.comp_files),
    ("-w"                , "-- turn warnings on for your script", f.comp_files),
    ("-x"                , "-- strip off text before #!ruby line and perhaps cd to directory", f.comp_files),
    (("-d", "--debug")   , "-- set debugging flags (set $DEBUG to true)", f.comp_files),
    (("-h", "--help")    , "-- print help message", []),
    (("-v", "--verbose") , "-- print version number, then turn on verbose mode", f.comp_files),
    (("-y", "--yydebug") , "-- enable yacc debugging in the parser", f.comp_files),
    ("--copyright"       , "-- print the copyright", []),
    ("--version"         , "-- print the version", f.comp_files),
    )

def _ruby_library():
    rubyeval = "puts $:"
    try:
        paths = subprocess.Popen(
            ["ruby", "-e", rubyeval],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()[0]
    except Exception:
        return []
    try:
        paths = paths.decode()
    except UnicodeError:
        return []

    library = []
    for path in paths.splitlines():
        try:
            entries = os.listdir(path)
        except OSError:
            continue
        for lib in entries:
            if os.path.isdir(os.path.join(path, lib)):
                lib += os.sep
            library.append(lib)
    library.sort()
    return library

class Ruby(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _ruby_arguments(self)]

    def default(self):
        return self.comp_files()

completion.register("ruby", Ruby)
