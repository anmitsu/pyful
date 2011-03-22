# util.py - utility functions
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
import re
import unicodedata

try:
    unicode
    def U(string):
        return string.decode('utf-8')

    def force_decode(string):
        try:
            return string.decode('utf-8')
        except UnicodeError:
            try:
                return string.decode('cp932')
            except UnicodeError:
                return string.decode('ascii')
except:
    def U(string):
        string.encode('utf-8')
        return string
    def force_decode(string):
        return string

def cmp_to_key(_cmp):
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return _cmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return _cmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return _cmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return _cmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return _cmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return _cmp(self.obj, other.obj) != 0
    return K

def cmp(x, y):
    return (x > y) - (x < y)

def uniq(ls):
    out = []
    for m in ls:
        if not m in out:
            out.append(m)
    return out

def flatten(ls):
    if isinstance(ls, list):
        for i in range(len(ls)):
            for e in flatten(ls[i]):
                yield e
    else:
        yield ls


def shlex_unicode(string):
    return [i.strip('"').strip("'") for i in re.split(r'(\s+|(?<!\\)".*?(?<!\\)"|(?<!\\)\'.*?(?<!\\)\')', string) if i.strip()]

def string_to_safe(string):
    return re.sub("([\s!\"#\$&'\(\)~\|\[\]\{\}\*;\?<>])", r"\\\1", string)

def quote(string):
    if re.search("[']", string):
        return '"{0}"'.format(string)
    elif re.search("[\"]", string):
        return "'{0}'".format(string)
    elif re.search("[\s!\#\$&\(\)~\|\[\]\{\}\*;\?<>]", string):
        return '"{0}"'.format(string)
    else:
        return string

def escapemacro(string):
    return re.sub(r"((?<!\\)%[mMdDfFxX])", r"\\\1", string)

def expandmacro(string, shell=False):
    from pyful import ui
    filer = ui.getcomponent("Filer")
    m = {
        "%m": re.search(r"(?<!\\)%m", string),
        "%M": re.search(r"(?<!\\)%M", string),
        "%d": re.search(r"(?<!\\)%d(?!2)", string),
        "%d2": re.search(r"(?<!\\)%d2", string),
        "%D": re.search(r"(?<!\\)%D(?!2)", string),
        "%D2": re.search(r"(?<!\\)%D2", string),
        "%f": re.search(r"(?<!\\)%f", string),
        "%F": re.search(r"(?<!\\)%F", string),
        "%x": re.search(r"(?<!\\)%x", string),
        "%X": re.search(r"(?<!\\)%X", string),
        }
    def _replace(pattern, repl, string):
        repl = escapemacro(repl)
        if (m["%m"] and pattern is m["%m"].re) or (m["%M"] and pattern is m["%M"].re):
            pass
        elif shell:
            repl = quote(repl)
        return pattern.sub(repl, string)

    if m["%m"]:
        marks = ""
        for f in filer.dir.get_mark_files():
            if shell:
                marks += string_to_safe(f) + ' '
            else:
                marks += f + ' '
        string = _replace(m["%m"].re, marks[:-1], string)
    if m["%M"]:
        marks = ""
        for f in filer.dir.get_mark_files():
            if shell:
                marks += string_to_safe(abspath(f)) + ' '
            else:
                marks += abspath(f) + ' '
        string = _replace(m["%M"].re, marks[:-1], string)
    if m["%d"]:
        path = unix_basename(filer.dir.path) + os.sep
        string = _replace(m["%d"].re, path, string)
    if m["%d2"]:
        path = unix_basename(filer.workspace.nextdir.path) + os.sep
        string = _replace(m["%d2"].re, path, string)
    if m["%D"]:
        path = filer.dir.path
        string = _replace(m["%D"].re, path, string)
    if m["%D2"]:
        path = filer.workspace.nextdir.path
        string = _replace(m["%D2"].re, path, string)
    if m["%f"]:
        path = filer.file.name
        string = _replace(m["%f"].re, path, string)
    if m["%F"]:
        path = abspath(filer.file.name)
        string = _replace(m["%F"].re, path, string)
    if m["%x"]:
        path = os.path.splitext(filer.file.name)[0]
        string = _replace(m["%x"].re, path, string)
    if m["%X"]:
        path = abspath(os.path.splitext(abspath(filer.file.name))[0])
        string = _replace(m["%X"].re, path, string)
    return re.sub(r"\\(%[mMdDfFxX])", r"\1", string)

def wait_restore():
    while 1:
        try:
            input("\nHIT ENTER KEY\n")
        except:
            pass
        break
    os.system("clear")


def mbslen(string):
    return len(U(string))

def insertstr(string, ins, length):
    string = U(string)
    f = string[:length]
    b = string[length:]
    return f + ins + b

def rmstr(string, length):
    string = U(string)
    f = string[:length]
    b = string[length+1:]
    return f + b

def slicestr(string, start, end):
    string = U(string)
    f = string[:start]
    b = string[end:]
    return f + b


def abspath(path, basedir=None):
    if basedir:
        return os.path.normpath(os.path.join(os.path.abspath(basedir), expanduser(path)))
    else:
        return os.path.abspath(expanduser(path))

def expanduser(path):
    if os.path.exists("~"):
        return path
    else:
        return os.path.expanduser(path)

def extname(path):
    root, ext = os.path.splitext(path)
    return ext

def unix_basename(path):
    return os.path.basename(path.rstrip(os.path.sep))

def unix_dirname(path):
    return os.path.dirname(path.rstrip(os.path.sep))

def path_omission(path, width):
    if termwidth(path) > width:
        for name in U(path).split(os.sep)[:-1]:
            if name:
                path = path.replace(name, name[0], 1)
            if termwidth(path) <= width:
                break
    return path

def termwidth(string, length=None):
    string = U(string)
    if length is None:
        length = len(string)
    string = string[:length]
    width = len(string)
    for c in string:
        if unicodedata.east_asian_width(c) in "WF":
            width += 1
    return width

def mbs_ljust(string, length, pad=" "):
    string = U(string)

    width = 0
    cut = False
    for i, c in enumerate(string):
        if length-1 <= width:
            string = string[0:i-1]
            cut = True
            break
        if unicodedata.east_asian_width(c) in "WF":
            width += 2
        else:
            width += 1
    if cut:
        space = length - termwidth(string)
    else:
        space = length - width
    if space > 0:
        string += pad * space
    return string

def mbs_rjust(string, length, pad=" "):
    string = U(string)
    width = 0
    cut = False
    for i, c in enumerate(reversed(string)):
        if length-1 <= width:
            string = string[len(string)-i:]
            cut = True
            break
        if unicodedata.east_asian_width(c) in "WF":
            width += 2
        else:
            width += 1
    if cut:
        space = length - termwidth(string)
    else:
        space = length - width
    if space > 0:
        string += pad * space
    return string
