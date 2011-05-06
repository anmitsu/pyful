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

def _cp_arguments(f): return (
    (("-a", "--archive")              , "", f.comp_files),
    ("--backup="                      , "", _backup_control),
    ("-b"                             , "", f.comp_files),
    ("--copy-contents"                , "", f.comp_files),
    ("-d"                             , "", f.comp_files),
    (("-f", "--force")                , "", f.comp_files),
    (("-i", "--interactive")          , "", f.comp_files),
    ("-H"                             , "", f.comp_files),
    (("-l", "--link")                 , "", f.comp_files),
    (("-L", "--dereference")          , "", f.comp_files),
    (("-n", "--no-clobber")           , "", f.comp_files),
    (("-P", "--no-dereference")       , "", f.comp_files),
    ("-p"                             , "", f.comp_files),
    ("--preserve="                    , "", _attr_list),
    ("--no-preserve="                 , "", _attr_list),
    ("--parents"                      , "", f.comp_files),
    (("-r", "-R", "--recursive")      , "", f.comp_files),
    ("--reflink"                      , "", f.comp_files),
    ("--remove-destination"           , "", f.comp_files),
    ("--sparse="                      , "", ["always", "auto", "never"]),
    ("--strip-trailing-slashes"       , "", f.comp_files),
    (("-s", "--symbolic-link")        , "", f.comp_files),
    (("-S", "--suffix")               , "", []),
    (("-t", "--target-directory=")    , "", f.comp_dirs),
    (("-T", "--no-target-directory=") , "", f.comp_dirs),
    (("-u", "--update")               , "", f.comp_files),
    (("-v", "--verbose")              , "", f.comp_files),
    (("-x", "--one-file-system")      , "", f.comp_files),
    ("--reply="                       , "", ["no", "query", "yes"]),
    ("--help"                         , "", f.comp_files),
    ("--version"                      , "", f.comp_files),
    )

def _backup_control():
    return ["existing", "never", "nil", "none", "numbered", "off", "simple", "t"]

def _attr_list():
    return ["all", "links", "mode", "ownership", "timestamps"]

class Cp(completion.ShellCompletionFunction):
    def __init__(self):
        self.arguments = [Argument(*item) for item in _cp_arguments(self)]

    def default(self):
        return self.comp_files()

completion.register("cp", Cp)
