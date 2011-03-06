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
import stat
import curses
import time
import threading
import pwd
import grp
import errno

from pyful import Pyful
from pyful import message
from pyful import process
from pyful import ui
from pyful import util

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
    filer = ui.getcomponent("Filer")
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

class Subloop(object):
    def __init__(self):
        self.cmdline = ui.getcomponent("Cmdline")
        self.filer = ui.getcomponent("Filer")
        self.menu = ui.getcomponent("Menu")
        self.message = ui.getcomponent("Message")
        self.stdscr = ui.getcomponent("Stdscr").win

    def subthreads_view(self):
        cmdscr = ui.getcomponent("Cmdscr").win
        y, x = cmdscr.getmaxyx()
        string = ""
        for i, t in enumerate(Filectrl.threads):
            string += "[%d] %s " % (i+1, t.title)
        cmdscr.move(0, 1)
        cmdscr.addstr(util.mbs_ljust(string, x-2), curses.A_BOLD)
        cmdscr.noutrefresh()

    def input(self, meta, key):
        if self.cmdline.is_active:
            self.cmdline.input(meta, key)
        elif self.menu.is_active:
            self.menu.input(meta, key)
        else:
            self.filer.input(meta, key)

    def view(self):
        self.filer.view()
        if self.menu.is_active:
            self.menu.view()
        if self.cmdline.is_active:
            self.cmdline.view()
        elif self.message.is_active:
            self.subthreads_view()
            self.message.view()
        else:
            self.subthreads_view()
        process.view_process()
        curses.doupdate()

    def run(self):
        self.stdscr.timeout(10)
        self.view()
        (meta, key) = ui.getch()
        if key != -1:
            self.input(meta, key)
        self.stdscr.timeout(-1)

class FilectrlCancel(Exception):
    pass

class Filectrl(object):
    threads = []
    event = threading.Event()

    def thread_loop(self, thread):
        self.threads.append(thread)
        self.event.set()
        thread.start()
        subloop = Subloop()
        while thread.isAlive():
            self.event.wait()
            subloop.run()
        if thread.error:
            message.exception(thread.error)
        else:
            message.puts("Thread finished: %s" % thread.title)
        self.threads.remove(thread)
        ui.getcomponent("Filer").workspace.all_reload()

    def delete(self, path):
        thread = DeleteThread(path)
        self.thread_loop(thread)

    def copy(self, src, dst):
        thread = CopyThread(src, dst)
        self.thread_loop(thread)

    def move(self, src, dst):
        thread = MoveThread(src, dst)
        self.thread_loop(thread)

    def tar(self, src, dst, tarmode='gzip', wrap=''):
        thread = TarThread(src, dst, tarmode, wrap)
        self.thread_loop(thread)

    def tareach(self, src, dst, tarmode='gzip', wrap=''):
        threadlist = []
        for f in src:
            path = os.path.join(dst, util.unix_basename(f))
            threadlist.append(TarThread(f, path, tarmode, wrap))
        for t in threadlist:
            self.thread_loop(t)
        message.puts("Finished 'tareach'")

    def untar(self, src, dstdir='.'):
        thread = UntarThread(src, dstdir)
        self.thread_loop(thread)

    def unzip(self, src, dstdir=''):
        thread = UnzipThread(src, dstdir)
        self.thread_loop(thread)

    def zip(self, src, dst, wrap):
        thread = ZipThread(src, dst, wrap)
        self.thread_loop(thread)

    def zipeach(self, src, dst, wrap):
        threadlist = []
        for f in src:
            path = os.path.join(dst, util.unix_basename(f))
            threadlist.append(ZipThread(f, path, wrap))
        for t in threadlist:
            self.thread_loop(t)
        message.puts("Finished 'zipeach'")

class JobThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.error = 0
        self.active = True
        self.title = self.__class__.__name__

    def run(self):
        pass

    def kill(self):
        pass

    def view_thread(self, status):
        message.puts(status, 0)
        curses.doupdate()

class TarThread(JobThread):
    tarmodes = {'tar': '', 'gzip': 'gz', 'bzip2': 'bz2'}
    tarexts = {'tar': '.tar', 'gzip': '.tgz', 'bzip2': '.bz2'}

    def __init__(self, src, dst, tarmode='gzip', wrap=''):
        JobThread.__init__(self)
        self.view_thread("Reading...")
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.U(os.getcwd()) + os.sep
            self.title = "Tar: mark files"
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
            self.title = "Tar: %s" % self.src
        self.dst = util.abspath(dst)
        ext = self.tarexts[tarmode]
        if not self.dst.endswith(ext):
            self.dst += ext
        self.tarmode = tarmode
        self.wrap = wrap

    def run(self):
        if not isinstance(self.src, list):
            if not os.path.exists(self.src):
                return message.error("No such file or directory - %s" % self.src)
        try:
            unicode
            self.dst = self.dst.encode()
        except:
            pass

        try:
            import tarfile
            mode = self.tarmodes[self.tarmode]
            tar = tarfile.open(self.dst, 'w|'+mode)
        except Exception as e:
            return message.exception(e)
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    if not os.path.exists(f):
                        message.error("No such file or directory - %s" % f)
                    else:
                        self.add(tar, f)
            else:
                self.add(tar, self.src)
        except FilectrlCancel as e:
            self.error = e
        finally:
            tar.close()
        if not isinstance(self.src, list):
            lst = os.lstat(self.src)
            os.utime(self.dst, (lst.st_mtime, lst.st_mtime))
        os.chmod(self.dst, 0o644)

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

    def add(self, tar, source):
        if os.path.isdir(source):
            self.add_file(tar, source)
            for root, dnames, fnames in os.walk(source):
                for name in fnames+dnames:
                    path = os.path.normpath(os.path.join(root, name))
                    self.add_file(tar, path)
        else:
            self.add_file(tar, source)

    def add_file(self, tar, source):
        arcname = source.replace(os.path.commonprefix([source, self.src_dirname]), '')
        self.view_thread("Adding: " + arcname)
        try:
            tar.add(source, os.path.join(self.wrap, arcname), recursive=False)
        except Exception as e:
            message.exception(e)
        if not self.active:
            raise FilectrlCancel("Tar canceled: %s" % arcname)

class UntarThread(JobThread):
    tarmodes = {'.tar': '', '.tgz': 'gz', '.gz': 'gz', '.bz2': 'bz2',}

    def __init__(self, src, dstdir='.'):
        JobThread.__init__(self)
        self.view_thread("Reading...")
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.title = "Untar: mark files"
        else:
            self.src = util.abspath(src)
            self.title = "Untar: %s" % self.src
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def run(self):
        if not os.access(self.dstdir, os.W_OK):
            self.error = OSError("No permission: %s" % self.dstdir)
            return
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self.extract(f)
            else:
                self.extract(self.src)
        except FilectrlCancel as e:
            self.error = e

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

    def extract(self, source):
        import tarfile
        mode = self.tarmodes.get(util.extname(source), 'gz')
        try:
            tar = tarfile.open(source, 'r:'+mode)
        except Exception as e:
            return message.exception(e)
        try:
            for info in tar.getmembers():
                if not self.active:
                    raise FilectrlCancel("Untar canceled: %s" % info.name)
                self.view_thread("Untar: " + info.name)
                tar.extract(info, self.dstdir)
                if info.isdir():
                    self.dirlist.append(info)
        finally:
            for dinfo in reversed(sorted(self.dirlist, key=lambda a: a.name)):
                dirpath = os.path.join(self.dstdir, dinfo.name) 
                os.utime(dirpath, (dinfo.mtime, dinfo.mtime))
            self.dirlist[:] = []
            tar.close()

class UnzipThread(JobThread):
    def __init__(self, src, dstdir=''):
        JobThread.__init__(self)
        self.view_thread('Reading...')
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.title = "Unzip: mark files"
        else:
            self.src = util.abspath(src)
            self.title = "Unzip: %s" % self.src
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def run(self):
        if not os.access(self.dstdir, os.W_OK):
            self.error = OSError("No permission: %s" % self.dstdir)
            return
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    self.extract(f)
            else:
                self.extract(self.src)
        except FilectrlCancel as e:
            self.error = e

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

    def extract(self, zippath):
        import zipfile
        try:
            myzip = zipfile.ZipFile(zippath, 'r')
        except Exception as e:
            return message.exception(e)
        try:
            for info in myzip.infolist():
                if not self.active:
                    raise FilectrlCancel("Unzip canceled: %s" % info.filename)
                try:
                    self.extract_file(myzip, info)
                except Exception as e:
                    message.exception(e)
        finally:
            for d in reversed(sorted(self.dirlist)):
                self.copy_external_attr(myzip, d)
            self.dirlist[:] = []
            myzip.close()

    def extract_file(self, myzip, zipinfo):
        fname = zipinfo.filename
        ufname = util.force_decode(fname)
        path = os.path.join(self.dstdir, ufname)

        if stat.S_ISDIR(zipinfo.external_attr >> 16):
            dirpath = os.path.join(self.dstdir, ufname)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            self.dirlist.append(fname)
        else:
            dirpath = os.path.join(self.dstdir, util.unix_dirname(ufname))
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            source = myzip.open(fname)
            target = open(path, 'wb')
            self.view_thread('Inflating: ' + ufname)
            shutil.copyfileobj(source, target)
            source.close()
            target.close()
            self.copy_external_attr(myzip, fname)

    def copy_external_attr(self, myzip, path):
        try:
            info = myzip.getinfo(path)
        except Exception as e:
            return message.exception(e)
        perm = info.external_attr >> 16
        date = list(info.date_time) + [-1, -1, -1]
        path = util.force_decode(path)
        abspath = os.path.join(self.dstdir, path)
        try:
            os.chmod(abspath, perm)
            atime = mtime = time.mktime(date)
            os.utime(abspath, (atime, mtime))
        except Exception as e:
            message.exception(e)

class ZipThread(JobThread):
    def __init__(self, src, dst, wrap=''):
        JobThread.__init__(self)
        self.view_thread('Reading...')
        if isinstance(src, list):
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.U(os.getcwd()) + os.sep
            self.title = "Zip: mark files"
        else:
            self.src = util.abspath(src)
            self.src_dirname = util.unix_dirname(self.src) + os.sep
            self.title = "Zip: %s" % self.src
        self.dst = util.abspath(dst)
        if not self.dst.endswith('.zip'):
            self.dst += '.zip'
        self.wrap = wrap

    def run(self):
        if not isinstance(self.src, list):
            if not os.path.exists(self.src):
                return message.error("No such file or directory - %s" % self.src)
        try:
            import zipfile
            myzip = zipfile.ZipFile(self.dst, 'w', compression=zipfile.ZIP_DEFLATED)
        except Exception as e:
            return message.exception(e)
        try:
            if isinstance(self.src, list):
                for f in self.src:
                    if not os.path.exists(f):
                        message.error("No such file or directory - %s" % f)
                    else:
                        self.write(myzip, f)
            else:
                self.write(myzip, self.src)
        except FilectrlCancel as e:
            self.error = e
        finally:
            myzip.close()

        if not isinstance(self.src, list):
            lst = os.lstat(self.src)
            os.utime(self.dst, (lst.st_mtime, lst.st_mtime))

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

    def write(self, myzip, source):
        if os.path.isdir(source):
            self.write_file(myzip, source)
            for root, dnames, fnames in os.walk(source):
                for name in fnames+dnames:
                    path = os.path.normpath(os.path.join(root, name))
                    self.write_file(myzip, path)
        else:
            self.write_file(myzip, source)

    def write_file(self, myzip, source):
        arcname = source.replace(os.path.commonprefix([source, self.src_dirname]), '')
        self.view_thread("Adding: " + arcname)
        try:
            myzip.write(source, os.path.join(self.wrap, arcname))
        except Exception as e:
            message.exception(e)
        if not self.active:
            raise FilectrlCancel("Zip canceled: %s" % arcname)

class DeleteThread(JobThread):
    def __init__(self, path):
        JobThread.__init__(self)
        if isinstance(path, list):
            self.title = "Delete: mark files"
            self.view_thread("Deleting: mark files")
            self.path = [util.abspath(f) for f in path]
        else:
            self.title = "Delete: %s" % path
            self.view_thread("Deleting: %s" % util.unix_basename(path))
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
            self.view_thread("Deleting: " + util.unix_basename(path))
            os.remove(path)
        else:
            dirlist = [path]
            for root, dirs, files in os.walk(path):
                for f in files:
                    self.view_thread("Deleting: " + f)
                    os.remove(os.path.join(root, f))
                    if not self.active:
                        raise FilectrlCancel("Delete canceled: %s" % f)
                for d in dirs:
                    dirlist.append(os.path.join(root, d))
            for d in reversed(sorted(dirlist)):
                if not os.access(path, os.R_OK) and not os.path.islink(path):
                    raise OSError("No permission: %s" % d)
                try:
                    os.rmdir(d)
                except Exception as e:
                    if e[0] == errno.ENOTEMPTY:
                        pass

class CopyThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.view_thread("Copy starting...")
        self.title = "Copy thread: %s" % self.name
        if isinstance(src, list):
            src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
        if dst.endswith(os.sep):
            dst = util.abspath(dst) + os.sep
        else:
            dst = util.abspath(dst)
        self.fjg = FileJobGenerator()
        self.jobs = self.fjg.generate(src, dst)

    def run(self):
        try:
            for job in self.jobs:
                if not self.active:
                    break
                if job:
                    job.copy(self)
        except FilectrlCancel as e:
            self.error = e
        self.fjg.copydirs()

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

class MoveThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.view_thread("Move starting...")
        self.title = "Move thread: %s" % self.name
        if isinstance(src, list):
            src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
        if dst.endswith(os.sep):
            dst = util.abspath(dst) + os.sep
        else:
            dst = util.abspath(dst)
        self.fjg = FileJobGenerator()
        self.jobs = self.fjg.generate(src, dst)

    def run(self):
        try:
            for job in self.jobs:
                if not self.active:
                    break
                if job:
                    job.move(self)
        except FilectrlCancel as e:
            self.error = e

        self.fjg.copydirs()

        self.fjg.dirlist.sort()
        self.fjg.dirlist.reverse()
        for d in self.fjg.dirlist:
            try:
                os.rmdir(d)
            except EnvironmentError as e:
                if e[0] == errno.ENOTEMPTY:
                    pass

    def kill(self):
        self.view_thread("Waiting...")
        self.active = False
        self.join()

class FileJobGenerator(object):
    def __init__(self):
        self.confirm = "importunate"
        self.dirlist = []
        self.dircopylist = []

    def generate(self, src, dst):
        def _checkfile(src, dst):
            ret = self.check_override(src, dst)
            if ret == "cancel":
                raise FilectrlCancel("Filejob canceled: %s -> %s" % (src, dst))
            if ret == "yes":
                return FileJob(src, dst)

        def _checkdir(src, dst):
            self.dirlist.append(src)
            if not os.path.isdir(dst):
                self.dircopylist.append((os.stat(src), dst))

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
                for checked in self.generate(f, dst):
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
            Filectrl.event.clear()
            sstat = os.stat(src)
            dstat = os.stat(dst)
            ssize = str(sstat.st_size)
            dsize = str(dstat.st_size)
            stime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(sstat.st_mtime))
            dtime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(dstat.st_mtime))
            msglist = ["source", "path: " + src, "size: " + ssize, "time: " + stime, "",
                       "destination", "path: " + dst, "size: " + dsize, "time: " + dtime]
            ret = message.confirm("Override?", ["Yes", "No", "Yes(all)", "No(all)", "Cancel"], msglist)
            Filectrl.event.set()
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

    def copydirs(self):
        for d in reversed(sorted(self.dircopylist)):
            try:
                os.makedirs(d[1])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            sst = d[0]
            dst = d[1]
            os.utime(dst, (sst.st_atime, sst.st_mtime))
            os.chmod(dst, stat.S_IMODE(sst.st_mode))

class FileJob(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def copysymlink(self, src, dst):
        if not os.path.islink(src):
            return
        linkto = os.readlink(src)
        os.symlink(linkto, dst)

    def copy(self, thread):
        try:
            if not os.path.isdir(util.unix_dirname(self.dst)):
                os.makedirs(util.unix_dirname(self.dst))

            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)

            thread.view_thread("Coping: " + util.unix_basename(self.src))

            if os.path.islink(self.src):
                self.copysymlink(self.src, self.dst)
            else:
                shutil.copyfile(self.src, self.dst)
                shutil.copystat(self.src, self.dst)
        except Exception as e:
            thread.error = e

    def move(self, thread):
        try:
            if not os.path.isdir(util.unix_dirname(self.dst)):
                os.makedirs(util.unix_dirname(self.dst))

            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)

            thread.view_thread("Moving: " + util.unix_basename(self.src))

            os.rename(self.src, self.dst)
        except EnvironmentError as e:
            if errno.EXDEV == e[0]:
                self.copy(thread)
                if thread.active:
                    try:
                        os.remove(self.src)
                    except EnvironmentError as e:
                        thread.error = e
            else:
                thread.error = e

