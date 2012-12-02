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
from pyful import util
from pyful import widget
from pyful import widgets

from pyful.widget.gauge import ProgressGauge

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
        ret = message.confirm(
            "{0}; Override? {{{1} -> {2}}}".format(os.strerror(errno.EEXIST), src, dst),
            ["Yes", "No", "Cancel"])
        if "Yes" != ret:
            return
    try:
        os.renames(src, dst)
        message.puts("Renamed: {0} -> {1}".format(src, dst))
    except Exception as e:
        message.exception(e)

def replace(pattern, repstr):
    filer = widgets.filer
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

    ret = ""
    for member in matched:
        src, dst = member
        if os.path.exists(os.path.join(filer.dir.path, dst)):
            if ret == "No(all)":
                continue
            if ret != "Yes(all)":
                ret = message.confirm(
                    "{0}; Override? {{{1} -> {2}}}".format(os.strerror(errno.EEXIST), src, dst),
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
    filer.dir.mark_clear()

def symlink(src, dst):
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, util.unix_basename(src))
        os.symlink(src, dst)
        message.puts("Created symlink: {0} -> {1}".format(src, dst))
    except Exception as e:
        message.exception(e)

def tar(src, dst, tarmode="gzip", wrap=""):
    Filectrl().tar(src, dst, tarmode, wrap)

def tareach(src, dst, tarmode="gzip", wrap=""):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().tareach(src, dst, tarmode, wrap)

def untar(src, dstdir):
    if not dstdir:
        dstdir = os.curdir + os.sep
    Filectrl().untar(src, dstdir)

def unzip(src, dstdir):
    if not dstdir:
        dstdir = os.curdir + os.sep
    Filectrl().unzip(src, dstdir)

def zip(src, dst, wrap=""):
    Filectrl().zip(src, dst, wrap)

def zipeach(src, dst, wrap=""):
    if not isinstance(src, list):
        return message.error("source must present `list'")
    Filectrl().zipeach(src, dst, wrap)


def kill_thread():
    try:
        thread = Filectrl.threads[0]
    except IndexError:
        return message.error("Thread doesn't exist.")
    title = thread.title
    ret = message.confirm("Kill {0}: ".format(title), ["OK", "Cancel"])
    if ret == "OK":
        thread.kill()

def _get_file_length(paths):
    flen = dlen = 0
    for path in paths:
        if not os.path.lexists(path):
            continue
        elif os.path.islink(path) or not os.path.isdir(path):
            flen += 1
        else:
            dlen += 1
            for root, dirs, files in os.walk(path):
                flen += len(files)
                dlen += len(dirs)
    return (flen, dlen)

class Subloop(object):
    def __init__(self):
        def _input(key):
            if widgets.cmdline.active:
                widgets.cmdline.input(key)
            elif widgets.menu.active:
                widgets.menu.input(key)
            elif widgets.help.active:
                widgets.help.input(key)
            else:
                widgets.filer.input(key)
        def _draw():
            widgets.filer.draw(navigation=False)
            if widgets.menu.active:
                widgets.menu.draw()
            if widgets.cmdline.active:
                widgets.cmdline.draw()
            elif widgets.help.active:
                widgets.helper.draw()
            else:
                if widgets.message.active and not widgets.filer.finder.active:
                    widgets.message.draw()
                self.draw_thread()
        self.navbar = widget.get("NavigationBar")
        self.ui = widget.ui.UI(_draw, _input)
        self.stdscr = widget.base.StandardScreen.stdscr

    def draw_thread(self):
        try:
            thread = Filectrl.threads[0]
            self.navbar.draw(thread.draw)
        except IndexError:
            return

    def run(self):
        util.global_synchro_event.wait()
        self.stdscr.timeout(100)
        self.ui.run()
        self.stdscr.timeout(-1)

class FilectrlCancel(Exception):
    pass

class Filectrl(object):
    threads = []

    def thread_loop(self, thread):
        self.threads.append(thread)
        thread.start()
        if len(self.threads) > 1:
            return
        subloop = Subloop()
        while len(self.threads):
            subloop.run()
        widgets.filer.workspace.all_reload()

    def delete(self, path):
        thread = DeleteThread(path)
        self.thread_loop(thread)

    def copy(self, src, dst):
        thread = CopyThread(src, dst)
        self.thread_loop(thread)

    def move(self, src, dst):
        thread = MoveThread(src, dst)
        self.thread_loop(thread)

    def tar(self, src, dst, tarmode="gzip", wrap=""):
        thread = TarThread(src, dst, tarmode, wrap)
        self.thread_loop(thread)

    def tareach(self, src, dst, tarmode="gzip", wrap=""):
        threadlist = []
        for f in src:
            path = os.path.join(dst, util.unix_basename(f))
            threadlist.append(TarThread(f, path, tarmode, wrap))
        for t in threadlist:
            self.thread_loop(t)
        message.puts("Finished 'tareach'")

    def untar(self, src, dstdir="."):
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
    lock = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.active = True
        self.title = self.__class__.__name__
        self.navbar = widget.get("NavigationBar")
        self.status = ""

    def main(self):
        pass

    def run(self):
        with self.lock:
            try:
                self.main()
                message.puts("Finished: {0}".format(self.title))
            except FilectrlCancel as e:
                message.exception(e)
            finally:
                Filectrl.threads.remove(self)

    def kill(self):
        self.update("Waiting...")
        self.active = False

    def draw(self, navbar):
        navbar.move(0, 1)
        navbar.clrtoeol()
        navbar.addstr(self.status, curses.A_BOLD)
        navbar.noutrefresh()

    def update(self, status):
        self.status = status

    def notify(self, notice):
        message.puts(notice)

class TarThread(JobThread):
    tarmodes = {"tar": "", "gzip": "gz", "bzip2": "bz2"}
    tarexts = {"tar": ".tar", "gzip": ".tgz", "bzip2": ".bz2"}

    def __init__(self, src, dst, tarmode="gzip", wrap=""):
        JobThread.__init__(self)
        self.update("Reading...")
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

    def main(self):
        try:
            unicode
            self.dst = self.dst.encode()
        except:
            pass
        try:
            import tarfile
            mode = self.tarmodes[self.tarmode]
            tar = tarfile.open(self.dst, "w|"+mode)
        except Exception as e:
            return message.exception(e)
        try:
            goal = sum(_get_file_length(self.src))
            elapse = 1
            for path in self.src:
                for f in self.generate(path):
                    arcname = f.replace(os.path.commonprefix([f, self.src_dirname]), "")
                    msg = "({0}/{1}): {2}".format(elapse, goal, arcname)
                    self.update("Adding{0}".format(msg))
                    self.add_file(tar, f, arcname)
                    self.notify("Added{0}".format(msg))
                    elapse += 1
        finally:
            tar.close()
        try:
            if len(self.src) == 1:
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

    def generate(self, path):
        if os.path.isdir(path):
            yield path
            for sub in os.listdir(path):
                for f in self.generate(os.path.join(path, sub)):
                    yield f
        else:
            yield path

class UntarThread(JobThread):
    tarmodes = {".tar": "", ".tgz": "gz", ".gz": "gz", ".bz2": "bz2",}

    def __init__(self, src, dstdir="."):
        JobThread.__init__(self)
        if isinstance(src, list):
            self.title = "Untar: mark files -> {0}".format(dstdir)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Untar: {0} -> {1}".format(src, dstdir)
            self.src = [util.abspath(src)]
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def main(self):
        self.update("Reading...")
        if not os.path.exists(self.dstdir):
            try:
                os.makedirs(self.dstdir)
            except OSError as e:
                return message.exception(e)
        for tarpath in self.src:
            self.extract(tarpath)

    def extract(self, source):
        mode = self.tarmodes.get(util.extname(source), "gz")
        try:
            import tarfile
            tar = tarfile.open(source, "r:"+mode)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while `untar'")
        try:
            for info in tar.getmembers():
                if not self.active:
                    raise FilectrlCancel(self.title)
                self.update("Extracting: {0}".format(info.name))
                tar.extract(info, self.dstdir)
                self.notify("Extracted: {0}".format(info.name))
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
        if isinstance(src, list):
            self.title = "Unzip: mark files -> {0}".format(dstdir)
            self.src = [util.abspath(f) for f in src]
        else:
            self.title = "Unzip: {0} -> {1}".format(src, dstdir)
            self.src = [util.abspath(src)]
        self.dstdir = util.abspath(dstdir)
        self.dirlist = []

    def main(self):
        self.update("Reading...")
        if not os.path.exists(self.dstdir):
            try:
                os.makedirs(self.dstdir)
            except OSError as e:
                return message.exception(e)
        for zippath in self.src:
            self.extract(zippath)

    def extract(self, zippath):
        try:
            import zipfile
            myzip = zipfile.ZipFile(zippath, "r")
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
            try:
                target = open(path, "wb")
                self.update("Inflating: {0}".format(ufname))
                shutil.copyfileobj(source, target)
                self.notify("Inflated: {0}".format(ufname))
                source.close()
                target.close()
                self.copy_external_attr(myzip, fname)
            except IOError as e:
                if e[0] == errno.EISDIR:
                    self.dirlist.append(fname)

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
    def __init__(self, src, dst, wrap=""):
        JobThread.__init__(self)
        if not dst.endswith(".zip"):
            dst += ".zip"
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

    def main(self):
        self.update("Reading...")
        try:
            mode = self.get_mode()
            import zipfile
            myzip = zipfile.ZipFile(self.dst, mode, compression=zipfile.ZIP_DEFLATED)
        except Exception as e:
            return message.exception(e)
        try:
            goal = sum(_get_file_length(self.src))
            elapse = 1
            for path in self.src:
                for f in self.generate(path):
                    arcname = f.replace(os.path.commonprefix([f, self.src_dirname]), "")
                    msg = "({0}/{1}): {2}".format(elapse, goal, arcname)
                    self.update("Adding{0}".format(msg))
                    self.write_file(myzip, f, arcname)
                    self.notify("Added{0}".format(msg))
                    elapse += 1
        finally:
            myzip.close()

        if len(self.src) == 1:
            try:
                lst = os.lstat(self.src[0])
                os.utime(self.dst, (lst.st_mtime, lst.st_mtime))
            except Exception as e:
                message.exception(e)

    def get_mode(self):
        if os.path.exists(self.dst):
            ret = message.confirm("Zip file exist - {0}:".format(self.dst),
                                  ["Add", "Override", "Cancel"])
            if ret == "Add":
                return "a"
            elif ret == "Override":
                return "w"
            else:
                raise FilectrlCancel("Zip canceled")
        else:
            return "w"

    def write_file(self, myzip, source, arcname):
        try:
            myzip.write(source, os.path.join(self.wrap, arcname))
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while `zip'")
        if not self.active:
            raise FilectrlCancel(self.title)

    def generate(self, path):
        if os.path.isdir(path):
            yield path
            for sub in os.listdir(path):
                for f in self.generate(os.path.join(path, sub)):
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
            path = util.abspath(path)
            self.title = "Delete: {0}".format(path)
            self.path = [path]

    def main(self):
        self.update("Delete starting...")
        goal = _get_file_length(self.path)[0]
        elapse = 1
        for path in self.path:
            for f in self.generate(path):
                msg = "({0}/{1}): {2}".format(elapse, goal, util.unix_basename(f))
                self.update("Deleting{0}".format(msg))
                self.delete_file(f)
                self.notify("Deleted{0}".format(msg))
                elapse += 1

    def delete_file(self, f):
        try:
            os.remove(f)
        except Exception as e:
            message.exception(e)
            raise FilectrlCancel("Exception occurred while deleting")
        if not self.active:
            raise FilectrlCancel(self.title)

    def delete_dir(self, directory):
        try:
            os.rmdir(directory)
        except Exception as e:
            if e[0] != errno.ENOTEMPTY:
                message.exception(e)
                raise FilectrlCancel("Exception occurred while directory deleting")

    def generate(self, path):
        if os.path.islink(path) or not os.path.isdir(path):
            yield path
        else:
            for sub in os.listdir(path):
                for f in self.generate(os.path.join(path, sub)):
                    yield f
            self.delete_dir(path)

class CopyThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.dst = util.abspath(dst)
        if dst.endswith(os.sep):
            self.dst += os.sep
        if isinstance(src, list):
            self.title = "Copy: mark files -> {0}".format(self.dst)
            self.src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
            self.title = "Copy: {0} -> {1}".format(src, self.dst)
            self.src = [src]

    def main(self):
        self.update("Copy starting...")
        goal = _get_file_length(self.src)[0]
        fjg = FileJobGenerator()
        elapse = 1
        mark = len(self.src) - 1
        for f in self.src:
            for job in fjg.generate(f, self.dst, False, mark):
                if not self.active:
                    raise FilectrlCancel(self.title)
                if job:
                    msg = "({0}/{1}): {2}".format(elapse, goal, util.unix_basename(job.src))
                    self.update("Copying{0}".format(msg))
                    job.copy()
                    self.notify("Copied{0}".format(msg))
                elapse += 1

class MoveThread(JobThread):
    def __init__(self, src, dst):
        JobThread.__init__(self)
        self.dst = util.abspath(dst)
        if dst.endswith(os.sep):
            self.dst += os.sep
        if isinstance(src, list):
            self.title = "Move: mark files -> {0}".format(self.dst)
            self.src = [util.abspath(f) for f in src]
        else:
            src = util.abspath(src)
            self.title = "Move: {0} -> {1}".format(src, self.dst)
            self.src = [src]

    def main(self):
        self.update("Move starting...")
        goal = _get_file_length(self.src)[0]
        fjg = FileJobGenerator()
        elapse = 1
        mark = len(self.src) - 1
        for f in self.src:
            for job in fjg.generate(f, self.dst, True, mark):
                if not self.active:
                    raise FilectrlCancel(self.title)
                if job:
                    msg = "({0}/{1}): {2}".format(elapse, goal, util.unix_basename(job.src))
                    self.update("Moving{0}".format(msg))
                    job.move()
                    self.notify("Moved{0}".format(msg))
                elapse += 1

class FileJobGenerator(object):
    def __init__(self):
        self.confirm = "Importunate"

    def generate(self, src, dst, moving, join=False):
        def _checkfile(src, dst):
            ret = self.check_override(src, dst)
            if ret == "Cancel":
                raise FilectrlCancel("Filejob canceled: {0} -> {1}".format(src, dst))
            if ret == "Yes":
                return FileJob(src, dst)

        def _checkdir(src, dst):
            copypair = None
            if not os.path.isdir(dst):
                copypair = (os.stat(src), dst)

            for f in os.listdir(src):
                ssub = os.path.join(src, f)
                dsub = os.path.join(dst, f)
                if os.path.isdir(ssub) and not os.path.islink(ssub):
                    for checked in _checkdir(ssub, dsub):
                        yield checked
                else:
                    yield _checkfile(ssub, dsub)
            if copypair:
                self.copydir(copypair)
            if moving:
                self.removedir(src)

        if join or os.path.isdir(dst) or dst.endswith(os.sep):
            dst = os.path.join(dst, util.unix_basename(src))

        if util.unix_dirname(dst).startswith(src):
            raise FilectrlCancel("Cannot copy/move a directory, `{0}', into itself, `{1}'".format(src, dst))

        if os.path.isdir(src) and not os.path.islink(src):
            for checked in _checkdir(src, dst):
                yield checked
        else:
            yield _checkfile(src, dst)

    def check_override(self, src, dst):
        if not os.path.lexists(dst) or \
                util.unix_basename(src) != util.unix_basename(dst):
            return "Yes"
        checked = None
        if "Yes(all)" == self.confirm:
            checked = "Yes"
        elif "No(all)" == self.confirm:
            checked = "No"
        elif "Newer(all)" == self.confirm:
            if os.lstat(src).st_mtime > os.lstat(dst).st_mtime:
                checked = "Yes"
            else:
                checked = "No"
        elif "Importunate" == self.confirm:
            sstat, dstat = os.lstat(src), os.lstat(dst)
            stime = time.strftime("%c", time.localtime(sstat.st_mtime))
            dtime = time.strftime("%c", time.localtime(dstat.st_mtime))
            ret = message.confirm(
                "Override?", ["Yes", "No", "Newer", "Yes(all)", "No(all)", "Newer(all)", "Cancel"],
                ["Source",
                 "Path: {0}".format(src),
                 "Size: {0}".format(sstat.st_size),
                 "Time: {0}".format(stime),
                 "Destination",
                 "Path: {0}".format(dst),
                 "Size: {0}".format(dstat.st_size),
                 "Time: {0}".format(dtime),])
            if ret == "Yes" or ret == "No" or ret == "Cancel":
                checked = ret
            elif ret == "Newer":
                if sstat.st_mtime > dstat.st_mtime:
                    checked = "Yes"
                else:
                    checked = "No"
            elif ret == "Yes(all)" or ret == "No(all)" or ret == "Newer(all)":
                self.confirm = ret
                checked = ret[:-5]
            else:
                checked = "Cancel"
        return checked

    def copydir(self, pair):
        try:
            os.makedirs(pair[1])
        except OSError as e:
            if e.errno != errno.EEXIST:
                message.exception(e)
        sst, dst = pair
        try:
            os.utime(dst, (sst.st_atime, sst.st_mtime))
            os.chmod(dst, stat.S_IMODE(sst.st_mode))
        except Exception as e:
            message.exception(e)

    def removedir(self, directory):
        try:
            os.rmdir(directory)
        except Exception as e:
            if e[0] != errno.ENOTEMPTY:
                message.exception(e)

class FileJob(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def copyfileobj(self, fsrc, fdst, length=16*1024):
        curval = 0
        navbar = widget.get("NavigationBar")
        size = os.stat(self.src).st_size
        if size:
            gauge = ProgressGauge(size)
        else:
            gauge = ProgressGauge(1)
        while True:
            buf = fsrc.read(length)
            if not buf:
                gauge.finish()
                if not widgets.cmdline.active:
                    navbar.draw(gauge.draw, 1, 1)
                break
            curval += len(buf)
            gauge.update(curval)
            if not widgets.cmdline.active:
                navbar.draw(gauge.draw, 1, 1)
            fdst.write(buf)

    def copyfile(self, src, dst):
        with open(src, "rb") as fsrc:
            with open(dst, "wb") as fdst:
                self.copyfileobj(fsrc, fdst)

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
                self.copyfile(self.src, self.dst)
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
