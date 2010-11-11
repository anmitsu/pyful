# filectrl.py - file management controller
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
import shutil
import curses
import time
import threading
import pwd
import grp
import errno

from pyfulib import util
from pyfulib.core import Pyful

pyful = Pyful()

def chmod(path, mode):
    try:
        os.chmod(path, int(mode, 8))
    except Exception as e:
        pyful.message.exception(e)

def chown(path, uid, gid):
    if not isinstance(uid, int):
        try:
            uid = pwd.getpwnam(uid)[2]
        except KeyError as e:
            pyful.message.exception(e)
            return
    if not isinstance(gid, int):
        try:
            gid = grp.getgrnam(gid)[2]
        except KeyError as e:
            pyful.message.exception(e)
            return
    try:
        os.chown(path, uid, gid)
    except EnvironmentError as e:
        pyful.message.exception(e)

def copy(src, dst):
    Filectrl().copy(src, dst)

def delete(path):
    try:
        if os.path.islink(path) or not os.path.isdir(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    except EnvironmentError as e:
        pyful.message.exception(e)

def link(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.link(src, dst)
    except EnvironmentError as e:
        pyful.message.exception(e)

def symlink(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.symlink(src, dst)
    except EnvironmentError as e:
        pyful.message.exception(e)

def mkdir(path, mode=0o755):
    try:
        os.makedirs(path, mode)
    except EnvironmentError as e:
        pyful.message.exception(e)

def mknod(path, mode=0o644):
    try:
        os.mknod(path, mode)
    except EnvironmentError as e:
        pyful.message.exception(e)

def move(src, dst):
    Filectrl().move(src, dst)

def replace(src, dst):
    buf = []
    for f in pyful.filer.dir.get_mark_files():
        try:
            buf.append(re.sub(src, r""+dst, f))
        except:
            return pyful.message.error("Regexp error")

    msg = []
    size = len(buf)

    for i in range(0, size):
        msg.append("%s -> %s" % (pyful.filer.dir.get_mark_files()[i], buf[i]))

    ret = pyful.message.confirm("Replace:", ["Start", "Cancel"], msg)
    if ret != "Start":
        return

    for i, src in enumerate(pyful.filer.dir.get_mark_files()):
        dst = buf[i]
        if src == dst:
            continue

        if os.path.exists(os.path.join(pyful.filer.dir.path, dst)):
            ret = pyful.message.confirm("File exist - (%s). Override?" % dst, ["Yes", "No"])
            if ret == "Yes":
                pass
            elif ret == "No" or ret is None:
                continue
        try:
            os.renames(src, dst)
        except EnvironmentError as e:
            pyful.message.exception(e)
            break

def unzip(src, dstdir=''):
    Filectrl().unzip(src, dstdir)

def zip(src, dst, wrap=''):
    Filectrl().zip(src, dst, wrap)

def tar(src, dst, tarmode='gzip', wrap=''):
    Filectrl().tar(src, dst, tarmode, wrap)

def untar(src, dstdir='.'):
    Filectrl().untar(src, dstdir)

def kill_thread():
    threads = list([str(th) for th in Filectrl.threads])
    if len(threads) == 0:
        pyful.message.error("Thread doesn't exist.")
        return
    ret = pyful.message.confirm("Kill thread: ", threads)
    for th in Filectrl.threads:
        if str(th) == ret:
            th.kill()

def view_threads():
    if pyful.cmdline.active or pyful.message.active:
        return
    pyful.stdscr.cmdwin.erase()
    pyful.stdscr.cmdwin.move(0, 1)
    for i, t in enumerate(Filectrl.threads):
        pyful.stdscr.cmdwin.addstr("[%s] %s " % (str(i+1), t.title), curses.A_BOLD)
    pyful.stdscr.cmdwin.move(1, pyful.stdscr.maxx-1)
    pyful.stdscr.cmdwin.noutrefresh()
    curses.doupdate()

class FilectrlCancel(Exception):
    pass

class Filectrl(object):
    threads = []

    def __init__(self):
        self.confirm = "importunate"
        self.thread = None
        self.jobs = None
        self.dirlist = []
        self.threadevent = threading.Event()

    def filejob_generator(self, src, dst):
        def _checkfile(src, dst):
            ret = self.check_override(src, dst)
            if ret == "cancel":
                raise FilectrlCancel
            if ret == "yes":
                return FileJob(src, dst)

        def _checkdir(src, dst):
            self.dirlist.append(src)

            for f in os.listdir(src):
                ssub = os.path.join(src, f)
                dsub = os.path.join(dst, f)
                if os.path.isdir(ssub) and not os.path.islink(ssub):
                    for checked in _checkdir(ssub, dsub):
                        yield checked
                else:
                    yield _checkfile(ssub, dsub)

        if isinstance(src, list):
            for f in src:
                for checked in self.filejob_generator(f, dst):
                    yield checked
        else:
            if dst.endswith(os.sep) or os.path.isdir(dst):
                dst = os.path.join(dst, util.unix_basename(src))

            if os.path.isdir(src) and not os.path.islink(src):
                for checked in _checkdir(src, dst):
                    yield checked
            else:
                yield _checkfile(src, dst)

    def check_override(self, src, dst):
        if not os.path.lexists(dst):
            return "yes"
        if not util.unix_basename(src) == util.unix_basename(dst):
            return "yes"

        if "importunate" == self.confirm:
            self.threadevent.clear()
            sstat = os.stat(src)
            dstat = os.stat(dst)
            ssize = str(sstat.st_size)
            dsize = str(dstat.st_size)
            stime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(sstat.st_mtime))
            dtime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(dstat.st_mtime))
            msglist = ["source", "path: " + src, "size: " + ssize, "time: " + stime, "",
                       "destination", "path: " + dst, "size: " + dsize, "time: " + dtime]
            ret = pyful.message.confirm("Override?", ["Yes", "No", "Yes(all)", "No(all)", "Cancel"], msglist)
            self.threadevent.set()
            if ret == "Yes":
                return "yes"
            elif ret == "No":
                return "no"
            elif ret == "Cancel":
                return "cancel"
            elif ret == "Yes(all)":
                self.confirm = "yes_all"
                return "yes"
            elif ret == "No(all)":
                self.confirm = "no_all"
                return "no"
            else:
                return "cancel"
        elif "yes_all" == self.confirm:
            return "yes"
        elif "no_all" == self.confirm:
            return "no"

    def thread_loop(self):
        Filectrl.threads.append(self.thread)
        pyful.view()
        self.threadevent.set()
        self.thread.start()
        while self.thread.isAlive():
            self.threadevent.wait()
            pyful.main_loop_nodelay()
        Filectrl.threads.remove(self.thread)
        pyful.filer.workspace.all_reload()
        pyful.view()

    def copy(self, src, dst):
        if isinstance(src, list):
            src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
        if dst.endswith(os.sep):
            dst = util.abspath(dst) + os.sep
        else:
            dst = util.abspath(dst)
        self.jobs = self.filejob_generator(src, dst)
        self.thread = CopyThread(self, "Copy")
        self.thread_loop()

    def move(self, src, dst):
        if isinstance(src, list):
            src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
        if dst.endswith(os.sep):
            dst = util.abspath(dst) + os.sep
        else:
            dst = util.abspath(dst)
        self.jobs = self.filejob_generator(src, dst)
        self.thread = MoveThread(self, "Move")
        self.thread_loop()

    def tar(self, src, dst, tarmode='gzip', wrap=''):
        self.thread = TarThread(src, dst, tarmode, wrap)
        self.thread_loop()

    def untar(self, src, dstdir='.'):
        self.thread = UntarThread(src, dstdir)
        self.thread_loop()

    def unzip(self, src, dstdir=''):
        self.thread = UnzipThread(src, dstdir)
        self.thread_loop()

    def zip(self, src, dst, wrap):
        self.thread = ZipThread(src, dst, wrap)
        self.thread_loop()

class TarThread(threading.Thread):
    tarmodes = {'tar': '', 'gzip': 'gz', 'bzip2': 'bz2'}
    tarexts = {'tar': '.tar', 'gzip': '.tgz', 'bzip2': '.bz2'}

    def __init__(self, src, dst, tarmode='gzip', wrap=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.active = True
        self.title = 'Reading...'
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.unistr(os.getcwd()) + os.sep
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
        self.dst = util.abspath(dst)
        self.tarmode = tarmode
        self.wrap = wrap

    def run(self):
        import tarfile
        mode = self.tarmodes[self.tarmode]
        ext = self.tarexts[self.tarmode]
        if not self.dst.endswith(ext):
            self.dst += ext

        try:
            unicode
            self.dst = self.dst.encode()
        except:
            pass

        try:
            tar = tarfile.open(self.dst, 'w|'+mode)
        except Exception as e:
            return pyful.message.exception(e)

        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self._add(tar, f)
            else:
                self._add(tar, self.src)
        except FilectrlCancel:
            pass
        tar.close()
        self.active = False

    def kill(self):
        self.title = "Waiting..."
        view_threads()
        self.active = False
        self.join()

    def _add(self, tar, source):
        if os.path.isdir(source):
            self.__add(tar, source)
            for root, dnames, fnames in os.walk(source):
                for name in fnames+dnames:
                    path = os.path.normpath(os.path.join(root, name))
                    self.__add(tar, path)
        else:
            self.__add(tar, source)

    def __add(self, tar, source):
        arcname = source.replace(os.path.commonprefix([source, self.src_dirname]), '')
        self.title = "Adding: " + arcname
        view_threads()
        tar.add(source, os.path.join(self.wrap, arcname), recursive=False)
        if not self.active:
            raise FilectrlCancel

class UntarThread(threading.Thread):
    tarmodes = {'.tar': '', '.tgz': 'gz', '.gz': 'gz', '.bz2': 'bz2',}

    def __init__(self, src, dstdir='.'):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.active = True
        self.title = 'Reading...'
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
        else:
            self.src = util.abspath(src)
        self.dstdir = util.abspath(dstdir)
        self.directories = []

    def run(self):
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self._extract(f)
            else:
                self._extract(self.src)
        except FilectrlCancel:
            pass

        self.directories.sort(key=lambda a: a.name)
        self.directories.reverse()
        for info in self.directories:
            dirpath = os.path.join(self.dstdir, info.name)
            os.utime(dirpath, (info.mtime, info.mtime))

        self.active = False

    def _extract(self, source):
        import tarfile
        mode = self.tarmodes.get(util.extname(source), 'gz')
        try:
            tar = tarfile.open(source, 'r:'+mode)
        except Exception as e:
            return pyful.message.exception(e)
        try:
            for info in tar.getmembers():
                if not self.active:
                    raise FilectrlCancel
                self.title = "Untar: " + info.name
                view_threads()
                tar.extract(info, self.dstdir)
                if info.isdir():
                    self.directories.append(info)
        finally:
            tar.close()

    def kill(self):
        self.title = "Waiting..."
        view_threads()
        self.active = False
        self.join()

class UnzipThread(threading.Thread):
    def __init__(self, src, dstdir=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.title = 'Unzip'
        self.active = True
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
        else:
            self.src = util.abspath(src)
        self.dstdir = util.abspath(dstdir)
        self.dirattrcopy = []

    def run(self):
        if isinstance(self.src, list):
            for f in self.src:
                self.extract(f)
        else:
            self.extract(self.src)
        for f in self.dirattrcopy:
            f()
        self.active = False

    def kill(self):
        self.title = "Waiting..."
        view_threads()
        self.active = False
        self.join()

    def copy_external_attr(self, myzip, path):
        try:
            info = myzip.getinfo(path+os.sep)
        except KeyError:
            try:
                info = myzip.getinfo(path)
            except KeyError:
                return
        perm = info.external_attr >> 16
        date = list(info.date_time) + [-1, -1, -1]
        path = util.force_decode(path)
        abspath = os.path.join(self.dstdir, path)
        os.chmod(abspath, perm)
        atime = mtime = time.mktime(date)
        os.utime(abspath, (atime, mtime))

    def makedirs(self, myzip, unipath, oripath, mode=0o755):
        abspath = os.path.join(self.dstdir, unipath)
        head, tail = os.path.split(abspath)
        if not tail:
            head, tail = os.path.split(head)
        if head and tail and not os.path.exists(head):
            try:
                self.makedirs(myzip, head, mode)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            if tail == os.curdir:
                return
        self.title = 'Creating: ' + unipath
        view_threads()
        os.mkdir(abspath, mode)
        self.dirattrcopy.append(lambda: self.copy_external_attr(myzip, oripath))

    def extract(self, srczippath):
        import zipfile

        try:
            myzip = zipfile.ZipFile(srczippath, 'r')
        except Exception as e:
            return pyful.message.exception(e)

        for info in myzip.infolist():
            if not self.active:
                break
            fname = info.filename
            unifname = util.force_decode(fname)
            try:
                path = os.path.join(self.dstdir, unifname)
            except UnicodeError:
                pyful.message.error("UnicodeError: Not support `%s' encoding" % fname)
                continue

            myzip_unidirname = util.unix_dirname(unifname)
            myzip_oridirname = util.unix_dirname(fname)
            if not os.path.isdir(os.path.join(self.dstdir, myzip_unidirname)):
                try:
                    self.makedirs(myzip, myzip_unidirname, myzip_oridirname)
                except OSError as e:
                    pyful.message.exception(e)
                    continue
            try:
                source = myzip.open(fname, pwd=path)
                target = open(path, 'wb')
                self.title = 'Inflating: ' + unifname
                view_threads()
                shutil.copyfileobj(source, target)
                source.close()
                target.close()
                self.copy_external_attr(myzip, fname)
            except IOError as e:
                if errno.EISDIR != e[0]:
                    pyful.message.exception(e)
                    continue
        myzip.close()

class ZipThread(threading.Thread):
    def __init__(self, src, dst, wrap=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.title = 'Zip'
        self.active = True
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.unistr(os.getcwd()) + os.sep
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
        self.dst = util.abspath(dst)
        self.wrap = wrap

    def run(self):
        import zipfile

        if not self.dst.endswith('.zip'):
            self.dst += '.zip'

        if not isinstance(self.src, list):
            if not os.path.exists(self.src):
                return pyful.message.error('No such file or directory (%s)' % self.src)

        try:
            myzip = zipfile.ZipFile(self.dst, 'w', compression=zipfile.ZIP_DEFLATED)
        except Exception as e:
            return pyful.message.exception(e)

        try:
            if isinstance(self.src, list):
                for path in self.src:
                    self.write(myzip, path)
            else:
                self.write(myzip, self.src)
        except FilectrlCancel:
            pass
        myzip.close()
        self.active = False

    def kill(self):
        self.title = "Waiting..."
        view_threads()
        self.active = False
        self.join()

    def _write(self, myzip, source):
        arcname = source.replace(os.path.commonprefix([source, self.src_dirname]), '')
        self.title = "Adding: " + arcname
        view_threads()
        myzip.write(source, os.path.join(self.wrap, arcname))
        if not self.active:
            raise FilectrlCancel

    def write(self, myzip, source):
        if os.path.isdir(source):
            self._write(myzip, source)
            for root, dnames, fnames in os.walk(source):
                for name in fnames+dnames:
                    path = os.path.normpath(os.path.join(root, name))
                    self._write(myzip, path)
        else:
            self._write(myzip, source)

class CopyThread(threading.Thread):
    def __init__(self, ctrl, title):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ctrl = ctrl
        self.title = title
        self.active = True

    def run(self):
        for j in self.ctrl.jobs:
            if not self.active:
                break
            if isinstance(j, FileJob):
                try:
                    j.copy(self)
                except FilectrlCancel:
                    pyful.message.error("Copy canceled")
                    break

    def kill(self):
        self.active = False

class MoveThread(threading.Thread):
    def __init__(self, ctrl, title):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ctrl = ctrl
        self.title = title
        self.active = True

    def run(self):
        for j in self.ctrl.jobs:
            if not self.active:
                break
            if isinstance(j, FileJob):
                try:
                    j.move(self)
                except FilectrlCancel:
                    pyful.message.error("Move canceled")
                    break

        def _sort(x, y):
            return util.cmp(len(y.split(os.sep)), len(x.split(os.sep)))

        self.ctrl.dirlist.sort(key=util.cmp_to_key(_sort))
        for d in self.ctrl.dirlist:
            try:
                os.rmdir(d)
            except EnvironmentError as e:
                if e[0] == errno.ENOTEMPTY:
                    pass

    def kill(self):
        self.active = False

class FileJob(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def copysymlink(self, src, dst):
        if not os.path.islink(src):
            return
        linkto = os.readlink(src)
        os.symlink(linkto, dst)

    def copyfileobj(self, src, dst, length=16*1024):
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while self.thread.active:
                    buf = fsrc.read(length)
                    if not buf:
                        break
                    fdst.write(buf)

    def makedirs(self, src, dst, mode=0o755):
        head, tail = os.path.split(dst)
        if not tail:
            head, tail = os.path.split(head)
        if head and tail and not os.path.exists(head):
            try:
                self.makedirs(util.unix_dirname(src), head, mode)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            if tail == os.curdir:
                return
        os.mkdir(dst, mode)
        if util.unix_basename(src) == util.unix_basename(dst):
            shutil.copystat(src, dst)

    def copydirs(self, src, dst):
        src = util.unix_dirname(self.src)
        dst = util.unix_dirname(self.dst)
        if not os.path.isdir(dst):
            self.makedirs(src, dst)

    def copy(self, thread):
        self.thread = thread
        try:
            self.copydirs(self.src, self.dst)

            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)

            thread.title = "Coping: " + util.unix_basename(self.src)
            view_threads()

            if os.path.islink(self.src):
                self.copysymlink(self.src, self.dst)
            else:
                self.copyfileobj(self.src, self.dst)
                shutil.copystat(self.src, self.dst)
        except Exception as e:
            pyful.message.exception(e)

    def move(self, thread):
        self.thread = thread
        try:
            self.copydirs(self.src, self.dst)

            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)

            thread.title = "Moving: " + util.unix_basename(self.src)
            view_threads()

            os.rename(self.src, self.dst)
        except EnvironmentError as e:
            if errno.EXDEV == e[0]:
                self.copy(thread)
                if thread.active:
                    delete(self.src)
            else:
                pyful.message.exception(e)

