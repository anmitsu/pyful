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

from pyful import completion
from pyful.completion import Argument

def _make_arguments(f): return (
    (("-b", "-m")                                         , "-- ugnored for compatibility", []),
    (("-B", "--always-make")                              , "-- unconditionally make all targets", []),
    (("-C", "--directory=")                               , "-- change to DIRECTORY before doing anything", f.comp_dirs),
    ("-d"                                                 , "-- print lots of debugging information", []),
    ("--debug"                                            , "-- print various types of debugging information", []),
    (("-e", "--environment-overrides")                    , "-- environment variables override makefiles", []),
    (("-f", "--file=", "--makefile=")                     , "-- read FILE as a makefile", f.comp_files),
    (("-h", "--help")                                     , "-- print this message and exit", []),
    (("-i", "--ignore-errors")                            , "-- ignore errors from commands", []),
    (("-I", "--include-dir=")                             , "-- search DIRECTORY for included makefiles", f.comp_dirs),
    (("-j", "--jobs")                                     , "-- allow N jobs at once", []),
    (("-k", "--keep-going")                               , "-- keep going when some targets can't be made", []),
    (("-l", "--load-average")                             , "-- don't start multiple jobs unless load is below N", []),
    (("-L", "--check-symlink-times")                      , "-- use the latest mtime between symlinks and target", []),
    (("-n", "--just-print", "--dry-run", "--recon")       , "-- don't actually run any commands", []),
    (("-o", "--old-file=", "--assume-old=")               , "-- consider FILE to be very old and don't remake it", f.comp_files),
    (("-p", "--print-data-base")                          , "-- print make's internal database", []),
    (("-q", "--question")                                 , "-- run no commands; exit status says if up to date", []),
    (("-r", "--no-builtin-rules")                         , "-- disable the built-in implicit rules", []),
    (("-R", "--no-builtin-variables")                     , "-- disable the built-in variable settings", []),
    (("-s", "--silent", "--quiet")                        , "-- don't echo commands", []),
    (("-S", "--no-keep-going", "--stop")                  , "-- turns off -k", []),
    (("-t", "--touch")                                    , "-- touch targets instead of remaking them", []),
    (("-v", "--version")                                  , "-- print the version number of make and exit", []),
    (("-w", "--print-directory")                          , "-- print the current directory", []),
    ("--no-print-directory"                               , "-- turn off -w, even if it was turned on implicitly", []),
    (("-W", "--what-if=", "--new-file=", "--assume-new=") , "-- consider FILE to be infinitely new", f.comp_files),
    ("--warn-undefined-variables"                         , "-- warn when an undefined variable is referenced", []),
    )

class Make(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _make_arguments(self)]

    def default(self):
        makefile = None
        for fname in ["GNUmakefile", "makefile", "Makefile"]:
            if os.path.exists(fname):
                makefile = fname
                break
        if not makefile:
            return []
        commands = []
        try:
            fd = open(makefile, "r")
        except OSError:
            return []
        current = self.parser.part[1]
        for line in fd:
            cols = line.split(":")
            if len(cols) == 2 and \
                    "$" not in cols[0] and \
                    "\t" not in cols[0] and \
                    not cols[0].startswith("#") and \
                    cols[0].startswith(current):
                commands.append(cols[0])
        commands.sort()
        return commands

completion.register("make", Make)
