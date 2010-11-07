# util.py - utility functions
#
# Copyright (C) 2010 anmitsu <anmitsu.s@gmail.com>
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
    def unistr(string):
        return string.decode()
except:
    def unistr(string):
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
    try:
        return (x > y) - (x < y)
    except UnicodeDecodeError:
        return 0

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


def string_to_safe(string):
    return re.sub("([\s!\"#\$&'\(\)~\|\[\]\{\}\*;\?<>])", r"\\\1", string)

def quote(string):
    if re.search("[']", string):
        return re.sub("^|$", '"', string)
    elif re.search("[\"]", string):
        return re.sub("^|$", "'", string)
    elif re.search("\s", string):
        return re.sub("^|$", '"', string)
    else:
        return string

def wait_restore():
    while 1:
        try:
            input("\nHIT ENTER KEY\n")
        except:
            pass
        break
    os.system("clear")


def mbslen(string):
    try:
        return len(unistr(string))
    except UnicodeDecodeError:
        return len(string)

def insertstr(string, ins, length):
    try:
        string = unistr(string)
    except UnicodeDecodeError:
        return string
    f = string[:length]
    b = string[length:]
    return f + ins + b

def rmstr(string, length):
    try:
        string = unistr(string)
    except UnicodeDecodeError:
        pass
    f = string[:length]
    b = string[length+1:]
    return f + b

def slicestr(string, start, end):
    try:
        string = unistr(string)
    except UnicodeDecodeError:
        pass
    f = string[:start]
    b = string[end:]
    return f + b


def abspath(path, basedir=None):
    if basedir:
        return os.path.normpath(os.path.join(os.path.abspath(basedir), path))
    else:
        return os.path.abspath(path)

def chdir(path):
    os.chdir(os.path.expanduser(path))

def extname(path):
    root, ext = os.path.splitext(path)
    return ext

def unix_basename(path):
    return os.path.basename(path.rstrip(os.path.sep))

def unix_dirname(path):
    return os.path.dirname(path.rstrip(os.path.sep))


def termwidth(string, length=None):
    try:
        string = unistr(string)
        if length is None:
            length = len(string)
        string = string[:length]
        width = len(string)
        for c in string:
            if unicodedata.east_asian_width(c) in "WF":
                width += 1
        return width
    except UnicodeDecodeError:
        return len(string)

def mbs_ljust(string, length, pad=" "):
    try:
        string = unistr(string)

        width = 0
        cut = False
        for i, c in enumerate(string):
            if length <= width:
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
    except UnicodeDecodeError:
        return string

def mbs_rjust(string, length, pad=" "):
    try:
        string = unistr(string)
        width = 0
        cut = False
        for i, c in enumerate(reversed(string)):
            if length <= width:
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
    except UnicodeDecodeError:
        return string
