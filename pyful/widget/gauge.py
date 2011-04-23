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

import curses
import time

from pyful import look
from pyful import util

class ProgressGauge(object):
    eta_format = "%H:%M:%S"
    units = ("B", "K", "M", "G", "T")

    def __init__(self, maxval):
        self.maxval = float(maxval)
        self.curval = 0.0
        self.start_time = None
        self.elapsed_time = 0.0

    def eta(self):
        try:
            eta = self.elapsed_time / self.curval * self.maxval - self.elapsed_time
        except ZeroDivisionError:
            return "unknown"
        eta_text = time.strftime(self.eta_format, time.gmtime(eta))
        return "ETA: {0}".format(eta_text)

    def bps(self):
        try:
            bps = self.curval / self.elapsed_time
        except ZeroDivisionError:
            bps = 0.0
        for unit in self.units:
            if bps < 1024:
                bps_text = "{0:>6.1f}{1}/s".format(bps, unit)
                break
            bps /= 1024
        return bps_text

    def update(self, value):
        self.curval = float(value)
        if not self.start_time:
            self.start_time = time.time()
        self.elapsed_time = time.time() - self.start_time

    def finish(self):
        self.update(self.maxval)

    def draw(self, win, y_offset=0, x_offset=0):
        y, x = win.getmaxyx()
        win.move(y_offset, x_offset)
        win.clrtoeol()
        rate = self.curval / self.maxval
        percent = int(rate * 100)

        status = "{0:>3}% |".format(percent)
        win.addstr(y_offset, x_offset, status)

        eta_status = "| {0} [{1}]".format(self.eta(), self.bps())
        eta_len = len(eta_status)

        width = x - x_offset - len(status) - eta_len
        pos = int(rate * width)

        gauge = " "*pos
        win.addstr(gauge, look.colors["ProgressGauge"])
        win.addstr(y_offset, x-eta_len, eta_status)
        win.noutrefresh()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    look.init_colors()
    stdscr.refresh()

    def test():
        maxval = 200*(1024**2)
        step = 7*1024

        gauge = ProgressGauge(maxval)
        for i in range(0, maxval+1, step):
            gauge.update(i)
            gauge.draw(stdscr)
            curses.doupdate()
        gauge.finish()
        gauge.draw(stdscr)
        curses.doupdate()
        stdscr.addstr("\nFinish!")
        stdscr.getch()

    try:
        test()
    except (SystemExit, KeyboardInterrupt):
        pass
    finally:
        curses.endwin()
