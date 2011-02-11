# filectrl.py - file management controller
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
import shutil
import curses
import time
import threading
import pwd
import grp
import errno

from pyful import Pyful
from pyful import message
from pyful import util
from pyful.filer import Filer

def chmod(path, mode):
    try:
        os.chmod(path, int(mode, 8))
        message.puts("Changed mode: %s -> %s" % (path, mode))
    except Exception as e:
        message.exception(e)

def chown(path, uid, gid):
    if not isinstance(uid, int):
        try:
            uid = pwd.getpwnam(uid)[2]
        except KeyError as e:
            message.exception(e)
            return
    if not isinstance(gid, int):
        try:
            gid = grp.getgrnam(gid)[2]
        except KeyError as e:
            message.exception(e)
            return
    try:
        os.chown(path, uid, gid)
        message.puts("Changed owner: %s: uid -> %s, gid -> %s" % (path, uid, gid))
    except EnvironmentError as e:
        message.exception(e)

def copy(src, dst):
    Filectrl().copy(src, dst)

def delete(path):
    Filectrl().delete(path)

def link(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.link(src, dst)
        message.puts("Created hard links: %s -> %s" % (src, dst))
    except EnvironmentError as e:
        message.exception(e)

def symlink(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.symlink(src, dst)
        message.puts("Created symlink: %s -> %s" % (src, dst))
    except EnvironmentError as e:
        message.exception(e)

def mkdir(path, mode=0o755):
    try:
        os.makedirs(path, mode)
        message.puts("Created directory: %s (%o)" % (path, mode))
    except EnvironmentError as e:
        message.exception(e)

def mknod(path, mode=0o644):
    try:
        os.mknod(path, mode)
        message.puts("Created file: %s (%o)" % (path, mode))
    except EnvironmentError as e:
        message.exception(e)

def move(src, dst):
    Filectrl().move(src, dst)

def rename(src, dst):
    if os.path.exists(dst) and os.path.samefile(src, dst):
        return
    if os.path.exists(dst):
        ret = message.confirm("File exist - (%s). Override?" % dst, ["Yes", "No", "Cancel"])
        if ret == "Yes":
            pass
        else:
            return
    try:
        os.renames(src, dst)
        message.puts("Renamed: %s -> %s" % (src, dst))
    except Exception as e:
        message.exception(e)

def replace(pattern, repstr):
    filer = Filer()
    files = filer.dir.get_mark_files()
    renamed = [pattern.sub(r""+repstr, f) for f in files]

    msg = []
    matched = []
    for i in range(0, len(files)):
        if files[i] != renamed[i]:
            msg.append("%s -> %s" % (files[i], renamed[i]))
            matched.append((files[i], renamed[i]))
    if not matched:
        return message.error("No pattern matched for mark files: %s " % pattern.pattern)

    ret = message.confirm("Replace:", ["Start", "Cancel"], msg)
    if ret != "Start":
        return

    for member in matched:
        src = member[0]
        dst = member[1]
        if os.path.exists(os.path.join(filer.dir.path, dst)):
            if ret == "No(all)":
                continue
            if ret != "Yes(all)":
                ret = message.confirm("File exist - (%s). Override?" % dst, ["Yes", "No", "Yes(all)", "No(all)", "Cancel"])
                if ret == "Yes" or ret == "Yes(all)":
                    pass
                elif ret == "No" or ret == "No(all)":
                    continue
                elif ret is None or ret == "Cancel":
                    break
        try:
            os.renames(src, dst)
            message.puts("Renamed: %s -> %s" % (src, dst))
        except EnvironmentError as e:
            message.exception(e)
            break

def unzip(src, dstdir=''):
    Filectrl().unzip(src, dstdir)

def zip(src, dst, wrap=''):
    Filectrl().zip(src, dst, wrap)

def zipeach(src, dst, wrap=''):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().zipeach(src, dst, wrap)

def tar(src, dst, tarmode='gzip', wrap=''):
    Filectrl().tar(src, dst, tarmode, wrap)

def tareach(src, dst, tarmode='gzip', wrap=''):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().tareach(src, dst, tarmode, wrap)

def untar(src, dstdir='.'):
    Filectrl().untar(src, dstdir)

def kill_thread():
    if len(Filectrl.threads) == 0:
        message.error("Thread doesn't exist.")
        return
    ret = message.confirm("Kill thread: ", [t.title for t in Filectrl.threads])
    for th in Filectrl.threads:
        if th.title == ret:
            th.kill()

def view_threads():
    for i, t in enumerate(Filectrl.threads):
        message.puts("[%s] %s" % (str(i+1), t.status), 0)
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
                raise FilectrlCancel("Filejob canceled: %s -> %s" % (src, dst))
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
            ret = message.confirm("Override?", ["Yes", "No", "Yes(all)", "No(all)", "Cancel"], msglist)
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
        self.threadevent.set()
        self.thread.start()
        main = Pyful()
        while self.thread.isAlive():
            self.threadevent.wait()
            main.main_loop_nodelay()
        if self.thread.error:
            message.exception(self.thread.error)
        else:
            message.puts("Thread finished: %s" % self.thread.title)
        Filectrl.threads.remove(self.thread)
        Filer().workspace.all_reload()

    def delete(self, path):
        self.thread = DeleteThread(path)
        self.thread_loop()

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
        self.thread = CopyThread(self)
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
        self.thread = MoveThread(self)
        self.thread_loop()

    def tar(self, src, dst, tarmode='gzip', wrap=''):
        self.thread = TarThread(src, dst, tarmode, wrap)
        self.thread_loop()

    def tareach(self, src, dst, tarmode='gzip', wrap=''):
        threadlist = []
        for f in src:
            path = os.path.join(dst, util.unix_basename(f))
            threadlist.append(TarThread(f, path, tarmode, wrap))
        for t in threadlist:
            self.thread = t
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

    def zipeach(self, src, dst, wrap):
        threadlist = []
        for f in src:
            path = os.path.join(dst, util.unix_basename(f))
            threadlist.append(ZipThread(f, path, wrap))
        for t in threadlist:
            self.thread = t
            self.thread_loop()

class TarThread(threading.Thread):
    tarmodes = {'tar': '', 'gzip': 'gz', 'bzip2': 'bz2'}
    tarexts = {'tar': '.tar', 'gzip': '.tgz', 'bzip2': '.bz2'}

    def __init__(self, src, dst, tarmode='gzip', wrap=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.active = True
        self.status = "Reading..."
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.unistr(os.getcwd()) + os.sep
            self.title = "Tar: mark files"
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
            self.title = "Tar: %s" % self.src
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
            self.error = e
            return 

        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self._add(tar, f)
            else:
                self._add(tar, self.src)
        except FilectrlCancel as e:
            self.error = e
        tar.close()

        if not isinstance(self.src, list):
            lst = os.lstat(self.src)
            os.utime(self.dst, (lst.st_mtime, lst.st_mtime))
        os.chmod(self.dst, 0o644)

        self.active = False

    def kill(self):
        self.status = "Waiting..."
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
        self.status = "Adding: " + arcname
        view_threads()
        tar.add(source, os.path.join(self.wrap, arcname), recursive=False)
        if not self.active:
            raise FilectrlCancel("Tar canceled: %s" % arcname)

class UntarThread(threading.Thread):
    tarmodes = {'.tar': '', '.tgz': 'gz', '.gz': 'gz', '.bz2': 'bz2',}

    def __init__(self, src, dstdir='.'):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.active = True
        self.status = 'Reading...'
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.title = "Untar: mark files"
        else:
            self.src = util.abspath(src)
            self.title = "Untar: %s" % self.src
        self.dstdir = util.abspath(dstdir)
        self.directories = []

    def run(self):
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self._extract(f)
            else:
                self._extract(self.src)
        except FilectrlCancel as e:
            self.error = e

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
            self.error = e
            return 
        try:
            for info in tar.getmembers():
                if not self.active:
                    raise FilectrlCancel("Untar canceled: %s" % info.name)
                self.status = "Untar: " + info.name
                view_threads()
                tar.extract(info, self.dstdir)
                if info.isdir():
                    self.directories.append(info)
        finally:
            tar.close()

    def kill(self):
        self.status = "Waiting..."
        view_threads()
        self.active = False
        self.join()

class UnzipThread(threading.Thread):
    def __init__(self, src, dstdir=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.status = 'Reading...'
        self.active = True
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.title = "Unzip: mark files"
        else:
            self.src = util.abspath(src)
            self.title = "Unzip: %s" % self.src
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
        self.status = "Waiting..."
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
        except Exception as e:
            self.error = e
            return 
        perm = info.external_attr >> 16
        date = list(info.date_time) + [-1, -1, -1]
        path = util.force_decode(path)
        abspath = os.path.join(self.dstdir, path)
        if perm == 0:
            if os.path.isdir(abspath):
                perm = 0o755
            else:
                perm = 0o644
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
        self.status = 'Creating: ' + unipath
        view_threads()
        os.mkdir(abspath, mode)
        self.dirattrcopy.append(lambda: self.copy_external_attr(myzip, oripath))

    def extract(self, srczippath):
        import zipfile

        try:
            myzip = zipfile.ZipFile(srczippath, 'r')
        except Exception as e:
            self.error = e
            return 

        for info in myzip.infolist():
            if not self.active:
                break
            fname = info.filename
            unifname = util.force_decode(fname)
            try:
                path = os.path.join(self.dstdir, unifname)
            except UnicodeError:
                message.error("UnicodeError: Not support `%s' encoding" % fname)
                continue

            myzip_unidirname = util.unix_dirname(unifname)
            myzip_oridirname = util.unix_dirname(fname)
            if not os.path.isdir(os.path.join(self.dstdir, myzip_unidirname)):
                try:
                    self.makedirs(myzip, myzip_unidirname, myzip_oridirname)
                except OSError as e:
                    message.exception(e)
                    continue
            try:
                source = myzip.open(fname, pwd=path)
                target = open(path, 'wb')
                self.status = 'Inflating: ' + unifname
                view_threads()
                shutil.copyfileobj(source, target)
                source.close()
                target.close()
                self.copy_external_attr(myzip, fname)
            except IOError as e:
                if errno.EISDIR != e[0]:
                    message.exception(e)
                    continue
        myzip.close()

class ZipThread(threading.Thread):
    def __init__(self, src, dst, wrap=''):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.status = 'Reading...'
        self.active = True
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.unistr(os.getcwd()) + os.sep
            self.title = "Zip: mark files"
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
            self.title = "Zip: %s" % self.src
        self.dst = util.abspath(dst)
        self.wrap = wrap

    def run(self):
        import zipfile

        if not self.dst.endswith('.zip'):
            self.dst += '.zip'

        if not isinstance(self.src, list):
            if not os.path.exists(self.src):
                return message.error('No such file or directory (%s)' % self.src)

        try:
            myzip = zipfile.ZipFile(self.dst, 'w', compression=zipfile.ZIP_DEFLATED)
        except Exception as e:
            self.error = e
            return 

        try:
            if isinstance(self.src, list):
                for path in self.src:
                    self.write(myzip, path)
            else:
                self.write(myzip, self.src)
        except FilectrlCancel as e:
            self.error = e
        myzip.close()

        if not isinstance(self.src, list):
            lst = os.lstat(self.src)
            os.utime(self.dst, (lst.st_mtime, lst.st_mtime))

        self.active = False

    def kill(self):
        self.status = "Waiting..."
        view_threads()
        self.active = False
        self.join()

    def _write(self, myzip, source):
        arcname = source.replace(os.path.commonprefix([source, self.src_dirname]), '')
        self.status = "Adding: " + arcname
        view_threads()
        myzip.write(source, os.path.join(self.wrap, arcname))
        if not self.active:
            raise FilectrlCancel("Zip canceled: %s" % arcname)

    def write(self, myzip, source):
        if os.path.isdir(source):
            self._write(myzip, source)
            for root, dnames, fnames in os.walk(source):
                for name in fnames+dnames:
                    path = os.path.normpath(os.path.join(root, name))
                    self._write(myzip, path)
        else:
            self._write(myzip, source)

class DeleteThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.active = True
        if isinstance(path, list):
            self.title = "Delete: mark files"
            self.status = "Deleting: mark files"
            self.path = [util.abspath(f) for f in path]
        else:
            self.title = "Delete: %s" % path
            self.status = "Deleting: %s" % util.unix_basename(path)
            self.path = util.abspath(path)

    def run(self):
        try:
            if isinstance(self.path, list):
                for f in self.path:
                    self.delete(f)
            else:
                self.delete(self.path)
        except Exception as e:
            self.error = e

    def kill(self):
        self.active = False

    def delete(self, path):
        if not os.access(path, os.R_OK) and not os.path.islink(path):
            raise OSError("No permission: %s" % path)
        if os.path.islink(path) or not os.path.isdir(path):
            self.status = "Deleting: " + util.unix_basename(path)
            view_threads()
            os.remove(path)
        else:
            dirlist = [path]
            for root, dirs, files in os.walk(path):
                for f in files:
                    self.status = "Deleting: " + f
                    view_threads()
                    os.remove(os.path.join(root, f))
                    if not self.active:
                        raise FilectrlCancel("Delete canceled: %s" % f)
                for d in dirs:
                    dirlist.append(os.path.join(root, d))
            dirlist.sort()
            dirlist.reverse()
            for d in dirlist:
                if not os.access(path, os.R_OK) and not os.path.islink(path):
                    raise OSError("No permission: %s" % d)
                try:
                    os.rmdir(d)
                except Exception as e:
                    if e[0] == errno.ENOTEMPTY:
                        pass

class CopyThread(threading.Thread):
    def __init__(self, ctrl):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.ctrl = ctrl
        self.status = "Copy starting..."
        self.title = "Copy thread: %s" % self.name
        self.active = True

    def run(self):
        try:
            for j in self.ctrl.jobs:
                if not self.active:
                    break
                if isinstance(j, FileJob):
                    j.copy(self)
        except FilectrlCancel as e:
            self.error = e

    def kill(self):
        self.active = False

class MoveThread(threading.Thread):
    def __init__(self, ctrl):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.ctrl = ctrl
        self.status = "Move starting..."
        self.title = "Move thread: %s" % self.name
        self.active = True

    def run(self):
        try:
            for j in self.ctrl.jobs:
                if not self.active:
                    break
                if isinstance(j, FileJob):
                    j.move(self)
        except FilectrlCancel as e:
            self.error = e

        self.ctrl.dirlist.sort()
        self.ctrl.dirlist.reverse()
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

            thread.status = "Coping: " + util.unix_basename(self.src)
            view_threads()

            if os.path.islink(self.src):
                self.copysymlink(self.src, self.dst)
            else:
                self.copyfileobj(self.src, self.dst)
                shutil.copystat(self.src, self.dst)
        except Exception as e:
            self.thread.error = e

    def move(self, thread):
        self.thread = thread
        try:
            self.copydirs(self.src, self.dst)

            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)

            thread.status = "Moving: " + util.unix_basename(self.src)
            view_threads()

            os.rename(self.src, self.dst)
        except EnvironmentError as e:
            if errno.EXDEV == e[0]:
                self.copy(thread)
                if thread.active:
                    try:
                        os.remove(self.src)
                    except EnvironmentError as e:
                        self.thread.error = e
            else:
                self.thread.error = e

