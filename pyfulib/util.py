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
    def unistr(string):
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


def string_to_safe(string):
    return re.sub("([\s!\"#\$&'\(\)~\|\[\]\{\}\*;\?<>])", r"\\\1", string)

def quote(string):
    if re.search("[']", string):
        return '"%s"' % string
    elif re.search("[\"]", string):
        return "'%s'" % string
    elif re.search("\s", string):
        return '"%s"' % string
    else:
        return string

def expandmacro(string, shell=False):
    ret = string
    from pyfulib.core import Pyful
    pyful = Pyful()

    marks = ''
    for f in pyful.filer.dir.get_mark_files():
        if shell:
            marks += string_to_safe(f) + ' '
        else:
            marks += f + ' '
    ret = re.sub('(?<!\\\\)%m', marks[:-1], ret)

    marks = ''
    for f in pyful.filer.dir.get_mark_files():
        if shell:
            marks += abspath(string_to_safe(f)) + ' '
        else:
            marks += abspath(f) + ' '
    ret = re.sub('(?<!\\\\)%M', marks[:-1], ret)

    filename = re.compile('(?<!\\\\)%d(?!2)')
    path = unix_basename(pyful.filer.dir.path) + os.sep
    if shell:
        ret = filename.sub(quote(path), ret)
    else:
        ret = filename.sub(path, ret)

    filename = re.compile('(?<!\\\\)%d2')
    path = unix_basename(pyful.filer.workspace.nextdir.path) + os.sep
    if shell:
        ret = filename.sub(quote(path), ret)
    else:
        ret = filename.sub(path, ret)

    filename = re.compile('(?<!\\\\)%D(?!2)')
    if shell:
        ret = filename.sub(quote(pyful.filer.dir.path), ret)
    else:
        ret = filename.sub(pyful.filer.dir.path, ret)

    filename = re.compile('(?<!\\\\)%D2')
    if shell:
        ret = filename.sub(quote(pyful.filer.workspace.nextdir.path), ret)
    else:
        ret = filename.sub(pyful.filer.workspace.nextdir.path, ret)

    filename = re.compile('(?<!\\\\)%f')
    if shell:
        ret = filename.sub(quote(pyful.filer.file.name), ret)
    else:
        ret = filename.sub(pyful.filer.file.name, ret)

    filename = re.compile('(?<!\\\\)%F')
    path = abspath(pyful.filer.file.name)
    if shell:
        ret = filename.sub(quote(path), ret)
    else:
        ret = filename.sub(path, ret)

    filename = re.compile('(?<!\\\\)%x')
    fname = unix_basename(pyful.filer.file.name)
    ext = extname(pyful.filer.file.name)
    if shell:
        ret = filename.sub(quote(fname.replace(ext, "")), ret)
    else:
        ret = filename.sub(fname.replace(ext, ""), ret)

    filename = re.compile('(?<!\\\\)%X')
    fname = unix_basename(pyful.filer.file.name)
    ext = extname(pyful.filer.file.name)
    fname = abspath(fname)
    if shell:
        ret = filename.sub(quote(fname.replace(ext, "")), ret)
    else:
        ret = filename.sub(fname.replace(ext, ""), ret)

    ret = re.sub('\\\\(%[mMdDfFxX])', r'\1', ret)
    return ret

def wait_restore():
    while 1:
        try:
            input("\nHIT ENTER KEY\n")
        except:
            pass
        break
    os.system("clear")


def mbslen(string):
    return len(unistr(string))

def insertstr(string, ins, length):
    string = unistr(string)
    f = string[:length]
    b = string[length:]
    return f + ins + b

def rmstr(string, length):
    string = unistr(string)
    f = string[:length]
    b = string[length+1:]
    return f + b

def slicestr(string, start, end):
    string = unistr(string)
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
    string = unistr(string)
    if length is None:
        length = len(string)
    string = string[:length]
    width = len(string)
    for c in string:
        if unicodedata.east_asian_width(c) in "WF":
            width += 1
    return width

def mbs_ljust(string, length, pad=" "):
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

def mbs_rjust(string, length, pad=" "):
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
