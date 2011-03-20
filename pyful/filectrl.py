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

from pyful import message
from pyful import process
from pyful import ui
from pyful import util

def chmod(path, mode):
    try:
        os.chmod(path, int(mode, 8))
        message.puts("Changed mode: {0} -> {1}".format(path, mode))
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
        message.puts("Changed owner: {0}: uid -> {1}, gid -> {2}".format(path, uid, gid))
    except Exception as e:
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
        message.puts("Created hard links: {0} -> {1}".format(src, dst))
    except Exception as e:
        message.exception(e)

def mkdir(path, mode=0o755):
    try:
        os.makedirs(path, mode)
        message.puts("Created directory: {0} ({1:#o})".format(path, mode))
    except Exception as e:
        message.exception(e)

def mknod(path, mode=0o644):
    try:
        os.mknod(path, mode)
        message.puts("Created file: {0} ({1:#o})".format(path, mode))
    except Exception as e:
        message.exception(e)

def move(src, dst):
    Filectrl().move(src, dst)

def rename(src, dst):
    if os.path.exists(dst) and os.path.samefile(src, dst):
        return
    if os.path.exists(dst):
        if "Yes" != message.confirm("File exist - ({0}). Override?".format(dst), ["Yes", "No", "Cancel"]):
            return
    try:
        os.renames(src, dst)
        message.puts("Renamed: {0} -> {1}".format(src, dst))
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
            msg.append("{0} -> {1}".format(files[i], renamed[i]))
            matched.append((files[i], renamed[i]))
    if not matched:
        return message.error("No pattern matched for mark files: {0} ".format(pattern.pattern))
    if "Start" != message.confirm("Replace:", ["Start", "Cancel"], msg):
        return

    ret = ''
    for member in matched:
        src, dst = member
        if os.path.exists(os.path.join(filer.dir.path, dst)):
            if ret == "No(all)":
                continue
            if ret != "Yes(all)":
                ret = message.confirm("File exist - ({0}). Override?".format(dst),
                                      ["Yes", "No", "Yes(all)", "No(all)", "Cancel"])
                if ret == "Yes" or ret == "Yes(all)":
                    pass
                elif ret == "No" or ret == "No(all)":
                    continue
                elif ret is None or ret == "Cancel":
                    break
        try:
            os.renames(src, dst)
            message.puts("Renamed: {0} -> {1}".format(src, dst))
        except Exception as e:
            message.exception(e)
            break

def symlink(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.symlink(src, dst)
        message.puts("Created symlink: {0} -> {1}".format(src, dst))
    except Exception as e:
        message.exception(e)

def tar(src, dst, tarmode='gzip', wrap=''):
    Filectrl().tar(src, dst, tarmode, wrap)

def tareach(src, dst, tarmode='gzip', wrap=''):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().tareach(src, dst, tarmode, wrap)

def untar(src, dstdir):
    if not dstdir:
        dstdir  = './'
    Filectrl().untar(src, dstdir)

def unzip(src, dstdir):
    if not dstdir:
        dstdir  = './'
    Filectrl().unzip(src, dstdir)

def zip(src, dst, wrap=''):
    Filectrl().zip(src, dst, wrap)

def zipeach(src, dst, wrap=''):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().zipeach(src, dst, wrap)


def kill_thread():
    if len(Filectrl.threads) == 0:
        return message.error("Thread doesn't exist.")
    ret = message.confirm("Kill thread: ", [t.title for t in Filectrl.threads])
    for th in Filectrl.threads:
        if th.title == ret:
            th.kill()

def get_file_length(*paths):
    flen = dlen = 0
    for path in paths:
        if not os.path.exists(path):
            continue
        elif not os.path.isdir(path):
            flen += 1
        else:
            dlen += 1
            for root, dirs, files in os.walk(path):
                flen += len(files)
                dlen += len(dirs)
    return (flen, dlen)

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
            string += "[{0}] {1} ".format(i+1, t.title)
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
        else:
            self.message.view()
            self.subthreads_view()
        process.view_process()
        curses.doupdate()

    def run(self):
        self.stdscr.timeout(100)
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
            message.puts("Thread finished: {0}".format(thread.title))
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

    def unzip(self, src, dstdir):
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
        self.view_thread("Waiting...")
        self.active = False

    def view_thread(self, status):
        message.puts(status, 0)

class TarThread(JobThread):
    tarmodes = {'tar': '', 'gzip': 'gz', 'bzip2': 'bz2'}
    tarexts = {'tar': '.tar', 'gzip': '.tgz', 'bzip2': '.bz2'}

    def __init__(self, src, dst, tarmode='gzip', wrap=''):
        JobThread.__init__(self)
        self.view_thread("Reading...")
        ext = self.tarexts[tarmode]
        if not dst.endswith(ext):
            dst += ext
        self.dst = util.abspath(dst)
        if isinstance(src, list):
            self.title = "Tar: mark files -> {0}".format(dst)
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.U(os.getcwd()) + os.sep
        else:
            self.title = "Tar: {0} -> {1}".format(src, dst)
            self.src = [util.abspath(src)]
            self.src_dirname = util.unix_dirname(self.src[0]) + os.sep
        self.tarmode = tarmode
        self.wrap = wrap

    def run(self):
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
            goal = sum(get_file_length(*self.src))
            elapse = 1
            for path in self.src:
                for f in self.addlist_generate(path):
                    arcname = f.replace(os.path.commonprefix([f, self.src_dirname]), '')
                    self.view_thread("Adding({0}/{1}): {2}".format(elapse, goal, arcname))
                    self.add_file(tar, f, arcname)
                    elapse += 1
        except FilectrlCancel as e:
            self.error = e
        finally:
            tar.close()
        try:
            if not self.error and len(self.src) == 1:
                lst = os.lstat(self.src[0])
                os.utime(self.dst, (lst.st_mtime, lst.st_mtime))
        except Exception as e:
            message.exception(e)

    def add_file(self, tar, source, arcname):
        try:
            tar.add(source, os.path.join(self.wrap, arcname), recursive=False)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while `tar'")
        if not self.active:
            raise FilectrlCancel(self.title)

    def addlist_generate(self, path):
        if os.path.isdir(path):
            yield path
            for sub in os.listdir(path):
                subpath = os.path.join(path, sub)
                for f in self.addlist_generate(subpath):
                    yield f
        else:
            yield path

class UntarThread(JobThread):
    tarmodes = {'.tar': '', '.tgz': 'gz', '.gz': 'gz', '.bz2': 'bz2',}

    def __init__(self, src, dstdir='.'):
        JobThread.__init__(self)
        self.view_thread("Reading...")
        if isinstance(src, list):
            self.title = "Untar: mark files -> {0}".format(dstdir)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Untar: {0} -> {1}".format(src, dstdir)
            self.src = [util.abspath(src)]
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def run(self):
        if not os.access(self.dstdir, os.W_OK):
            self.error = OSError("No permission: {0}".format(self.dstdir))
            return
        try:
            for tarpath in self.src:
                self.extract(tarpath)
        except FilectrlCancel as e:
            self.error = e

    def extract(self, source):
        mode = self.tarmodes.get(util.extname(source), 'gz')
        try:
            import tarfile
            tar = tarfile.open(source, 'r:'+mode)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while `untar'")
        try:
            for info in tar.getmembers():
                if not self.active:
                    raise FilectrlCancel(self.title)
                self.view_thread("Untar: {0}".format(info.name))
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
    def __init__(self, src, dstdir):
        JobThread.__init__(self)
        self.view_thread('Reading...')
        if isinstance(src, list):
            self.title = "Unzip: mark files -> {0}".format(dstdir)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Unzip: {0} -> {1}".format(src, dstdir)
            self.src = [util.abspath(src)]
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def run(self):
        if not os.access(self.dstdir, os.W_OK):
            self.error = OSError("No permission: {0}".format(self.dstdir))
            return
        try:
            for zippath in self.src:
                self.extract(zippath)
        except FilectrlCancel as e:
            self.error = e

    def extract(self, zippath):
        try:
            import zipfile
            myzip = zipfile.ZipFile(zippath, 'r')
        except Exception as e:
            return message.exception(e)
        try:
            for info in myzip.infolist():
                if not self.active:
                    raise FilectrlCancel(self.title)
                try:
                    self.extract_file(myzip, info)
                except Exception as e:
                    message.exception(e)
                    raise FilectrlCancel("Exception occurred while `unzip'")
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
            self.view_thread('Inflating: {0}'.format(ufname))
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
            if perm:
                os.chmod(abspath, perm)
            atime = mtime = time.mktime(date)
            os.utime(abspath, (atime, mtime))
        except Exception as e:
            message.exception(e)

class ZipThread(JobThread):
    def __init__(self, src, dst, wrap=''):
        JobThread.__init__(self)
        self.view_thread('Reading...')
        if not dst.endswith('.zip'):
            dst += '.zip'
        self.dst = util.abspath(dst)
        if isinstance(src, list):
            self.title = "Zip: mark files -> {0}".format(dst)
            self.src = [util.abspath(f) for f in src]
            self.src_dirname = util.U(os.getcwd()) + os.sep
        else:
            self.title = "Zip: {0} -> {1}".format(src, dst)
            self.src = [util.abspath(src)]
            self.src_dirname = util.unix_dirname(self.src[0]) + os.sep
        self.wrap = wrap

    def run(self):
        try:
            mode = self.get_mode()
            import zipfile
            myzip = zipfile.ZipFile(self.dst, mode, compression=zipfile.ZIP_DEFLATED)
        except Exception as e:
            self.error = e
            return
        try:
            goal = sum(get_file_length(*self.src))
            elapse = 1
            for path in self.src:
                for f in self.writelist_generate(path):
                    arcname = f.replace(os.path.commonprefix([f, self.src_dirname]), '')
                    self.view_thread("Adding({0}/{1}): {2}".format(elapse, goal, arcname))
                    self.write_file(myzip, f, arcname)
                    elapse += 1
        except FilectrlCancel as e:
            self.error = e
        finally:
            myzip.close()

        if not self.error and len(self.src) == 1:
            try:
                lst = os.lstat(self.src[0])
                os.utime(self.dst, (lst.st_mtime, lst.st_mtime))
            except Exception as e:
                message.exception(e)

    def get_mode(self):
        if os.path.exists(self.dst):
            Filectrl.event.clear()
            ret = message.confirm("Zip file exist - {0}:".format(self.dst),
                                  ['Add', 'Override', 'Cancel'])
            Filectrl.event.set()
            if ret == 'Add':
                return 'a'
            elif ret == 'Override':
                return 'w'
            else:
                raise FilectrlCancel('Zip canceled')
        else:
            return 'w'

    def write_file(self, myzip, source, arcname):
        try:
            myzip.write(source, os.path.join(self.wrap, arcname))
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while `zip'")
        if not self.active:
            raise FilectrlCancel(self.title)

    def writelist_generate(self, path):
        if os.path.isdir(path):
            yield path
            for sub in os.listdir(path):
                subpath = os.path.join(path, sub)
                for f in self.writelist_generate(subpath):
                    yield f
        else:
            yield path

class DeleteThread(JobThread):
    def __init__(self, path):
        JobThread.__init__(self)
        if isinstance(path, list):
            self.title = "Delete: mark files"
            self.path = [util.abspath(f) for f in path]
        else:
            self.title = "Delete: {0}".format(path)
            self.path = [util.abspath(path)]
        self.dirlist = []

    def run(self):
        goal = get_file_length(*self.path)[0]
        elapse = 1
        try:
            for path in self.path:
                for f in self.deletelist_generate(path):
                    self.view_thread("Deleting({0}/{1}): {2}".format(elapse, goal, util.unix_basename(f)))
                    self.delete_file(f)
                    elapse += 1
            self.delete_dirs()
        except FilectrlCancel as e:
            self.error = e

    def delete_file(self, f):
        try:
            os.remove(f)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while deleting")
        if not self.active:
            raise FilectrlCancel(self.title)

    def delete_dirs(self):
        for d in reversed(sorted(self.dirlist)):
            try:
                os.rmdir(d)
            except Exception as e:
                if e[0] != errno.ENOTEMPTY:
                    message.exception(e)
                    raise FilectrlCancel("Exception occurred while directory deleting")

    def deletelist_generate(self, path):
        if os.path.islink(path) or not os.path.isdir(path):
            yield path
        else:
            self.dirlist.append(path)
            for root, dirs, files in os.walk(path):
                for f in files:
                    yield os.path.join(root, f)
                for d in dirs:
                    self.dirlist.append(os.path.join(root, d))

class CopyThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.view_thread("Copy starting...")
        if isinstance(src, list):
            self.title = "Copy: mark files -> {0}".format(dst)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Copy: {0} -> {1}".format(src, dst)
            self.src = [util.abspath(src)]
        if dst.endswith(os.sep):
            self.dst = util.abspath(dst) + os.sep
        else:
            self.dst = util.abspath(dst)

    def run(self):
        goal = get_file_length(*self.src)[0]
        fjg = FileJobGenerator()
        elapse = 1
        try:
            for f in self.src:
                for job in fjg.generate(f, self.dst):
                    if not self.active:
                        raise FilectrlCancel(self.title)
                    if job:
                        self.view_thread("Coping({0}/{1}): {2}".format(elapse, goal, util.unix_basename(job.src)))
                        job.copy()
                    elapse += 1
        except FilectrlCancel as e:
            self.error = e
        fjg.copydirs()

class MoveThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.view_thread("Move starting...")
        if isinstance(src, list):
            self.title = "Move: mark files -> {0}".format(dst)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Move: {0} -> {1}".format(src, dst)
            self.src = [util.abspath(src)]
        if dst.endswith(os.sep):
            self.dst = util.abspath(dst) + os.sep
        else:
            self.dst = util.abspath(dst)

    def run(self):
        goal = get_file_length(*self.src)[0]
        fjg = FileJobGenerator()
        elapse = 1
        try:
            for f in self.src:
                for job in fjg.generate(f, self.dst):
                    if not self.active:
                        raise FilectrlCancel(self.title)
                    if job:
                        self.view_thread("Moving({0}/{1}): {2}".format(elapse, goal, util.unix_basename(job.src)))
                        job.move()
                    elapse += 1
        except FilectrlCancel as e:
            self.error = e
        fjg.copydirs()
        fjg.removedirs()

class FileJobGenerator(object):
    def __init__(self):
        self.confirm = "Importunate"
        self.dirlist = []
        self.dircopylist = []

    def generate(self, src, dst):
        def _checkfile(src, dst):
            ret = self.check_override(src, dst)
            if ret == "Cancel":
                raise FilectrlCancel("Filejob canceled: {0} -> {1}".format(src, dst))
            if ret == "Yes":
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

        if dst.endswith(os.sep) or os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        if os.path.isdir(src) and not os.path.islink(src):
            for checked in _checkdir(src, dst):
                yield checked
        else:
            yield _checkfile(src, dst)

    def check_override(self, src, dst):
        if not os.path.lexists(dst):
            return "Yes"
        if not util.unix_basename(src) == util.unix_basename(dst):
            return "Yes"
        if "Yes(all)" == self.confirm:
            return "Yes"
        elif "No(all)" == self.confirm:
            return "No"
        elif "Importunate" == self.confirm:
            Filectrl.event.clear()
            sstat, dstat = os.lstat(src), os.lstat(dst)
            stime = time.strftime("%c", time.localtime(sstat.st_mtime))
            dtime = time.strftime("%c", time.localtime(dstat.st_mtime))
            ret = message.confirm(
                "Override?", ["Yes", "No", "Yes(all)", "No(all)", "Cancel"],
                "Source{0}Path: {1}{0}Size: {2}{0}Time: {3}{0}{0}Destination{0}Path: {4}{0}Size: {5}{0}Time: {6}".format(
                    os.linesep, src, sstat.st_size, stime, dst, dstat.st_size, dtime).split(os.linesep)
                )
            Filectrl.event.set()
            if ret == "Yes" or ret == "No" or ret == "Cancel":
                return ret
            elif ret == "Yes(all)" or ret == "No(all)":
                self.confirm = ret
                return ret.replace("(all)", '')
            else:
                return "Cancel"

    def copydirs(self):
        for d in reversed(sorted(self.dircopylist)):
            try:
                os.makedirs(d[1])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    message.exception(e)
            sst, dst = d
            try:
                os.utime(dst, (sst.st_atime, sst.st_mtime))
                os.chmod(dst, stat.S_IMODE(sst.st_mode))
            except Exception as e:
                message.exception(e)

    def removedirs(self):
        for d in reversed(sorted(self.dirlist)):
            try:
                os.rmdir(d)
            except Exception as e:
                if e[0] != errno.ENOTEMPTY:
                    message.exception(e)

class FileJob(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def copysymlink(self, src, dst):
        if not os.path.islink(src):
            return
        linkto = os.readlink(src)
        os.symlink(linkto, dst)

    def copy(self):
        try:
            if not os.path.isdir(util.unix_dirname(self.dst)):
                os.makedirs(util.unix_dirname(self.dst))
            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)
            if os.path.islink(self.src):
                self.copysymlink(self.src, self.dst)
            else:
                shutil.copyfile(self.src, self.dst)
                shutil.copystat(self.src, self.dst)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while copying")

    def move(self):
        try:
            if not os.path.isdir(util.unix_dirname(self.dst)):
                os.makedirs(util.unix_dirname(self.dst))
            if os.path.isfile(self.dst):
                if not os.access(self.dst, os.W_OK):
                    os.remove(self.dst)
            os.rename(self.src, self.dst)
        except Exception as e:
            if errno.EXDEV == e[0]:
                self.copy()
                try:
                    os.remove(self.src)
                except Exception as e:
                    message.exception(e)
                    raise FilectrlCancel("Exception occurred while removing")
            else:
                message.exception(e)
                raise FilectrlCancel("Exception occurred while moving")
