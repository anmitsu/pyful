# look.py - a look management
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

import curses

colors = {}

__MARK__                = 1
__LINK__                = 2
__LINK_DIR__            = 19
__DIRECTORY__           = 3
__EXECUTABLE__          = 4
__MSG_PUTS__            = 5
__MSG_ERROR__           = 6
__MSG_CONFIRM__         = 7
__FINDER__              = 8
__WKS_SELECTED__        = 9
__CMDLINE_SEPARATOR__    = 10
__CMDLINE_OPTION__       = 11
__CMDLINE_PY_FUNCTION__ = 14
__CMDLINE_MACRO__        = 15
__CMDLINE_PROGRAM__      = 16
__CMDLINE_NO_PROGRAM__   = 17
__CMDLINE__              = 23
__CANDIDATE_HILIGHT__ = 24

__RED__   = 50
__MAGENTA__ = 51
__YELLOW__ = 52
__CYAN__ = 53
__BLUE__ = 54
__GREEN__ = 55

def init_colors():
    curses.init_pair(__RED__            , curses.COLOR_RED     , -1)
    curses.init_pair(__MAGENTA__        , curses.COLOR_MAGENTA    , -1)
    curses.init_pair(__YELLOW__         , curses.COLOR_YELLOW    , -1)
    curses.init_pair(__CYAN__           , curses.COLOR_CYAN       , -1)
    curses.init_pair(__BLUE__           , curses.COLOR_BLUE       , -1)
    curses.init_pair(__GREEN__          , curses.COLOR_GREEN        , -1)
    curses.init_pair(__MARK__                , curses.COLOR_YELLOW     , -1)
    curses.init_pair(__LINK__                , curses.COLOR_MAGENTA    , -1)
    curses.init_pair(__LINK_DIR__            , curses.COLOR_MAGENTA    , -1)
    curses.init_pair(__DIRECTORY__           , curses.COLOR_CYAN       , -1)
    curses.init_pair(__EXECUTABLE__          , curses.COLOR_RED        , -1)
    curses.init_pair(__MSG_PUTS__            , -1                      , -1)
    curses.init_pair(__MSG_ERROR__           , curses.COLOR_RED        , -1)
    curses.init_pair(__MSG_CONFIRM__         , curses.COLOR_CYAN       , -1)
    curses.init_pair(__FINDER__              , curses.COLOR_BLACK      , curses.COLOR_CYAN)
    curses.init_pair(__WKS_SELECTED__        , curses.COLOR_BLACK      , curses.COLOR_CYAN)
    curses.init_pair(__CMDLINE_SEPARATOR__    , curses.COLOR_BLUE       , -1)
    curses.init_pair(__CMDLINE_OPTION__       , curses.COLOR_YELLOW     , -1)
    curses.init_pair(__CMDLINE_PY_FUNCTION__ , curses.COLOR_CYAN       , -1)
    curses.init_pair(__CMDLINE_MACRO__        , curses.COLOR_MAGENTA    , -1)
    curses.init_pair(__CMDLINE_PROGRAM__      , curses.COLOR_GREEN      , -1)
    curses.init_pair(__CMDLINE_NO_PROGRAM__   , curses.COLOR_RED        , -1)
    curses.init_pair(__CMDLINE__              , curses.COLOR_CYAN       , -1)
    curses.init_pair(__CANDIDATE_HILIGHT__   , curses.COLOR_BLUE     , -1)

    colors.update({
            'RED': curses.color_pair(__RED__),
            'MAGENTA': curses.color_pair(__MAGENTA__),
            'YELLOW': curses.color_pair(__YELLOW__),
            'CYAN': curses.color_pair(__CYAN__),
            'BLUE': curses.color_pair(__BLUE__),
            'GREEN': curses.color_pair(__GREEN__),
            'CANDIDATE_HILIGHT': curses.A_BOLD,
            'MARK': curses.color_pair(__MARK__) | curses.A_BOLD,
            'LINK': curses.color_pair(__LINK__),
            'LINKDIR': curses.color_pair(__LINK_DIR__) | curses.A_BOLD,
            'DIRECTORY': curses.color_pair(__DIRECTORY__) | curses.A_BOLD,
            'EXECUTABLE': curses.color_pair(__EXECUTABLE__) | curses.A_BOLD,
            'MSGPUT': curses.color_pair(__MSG_PUTS__),
            'MSGERR': curses.color_pair(__MSG_ERROR__) | curses.A_BOLD,
            'MSGCONFIRM': curses.color_pair(__MSG_CONFIRM__) | curses.A_BOLD,
            'FINDER': curses.color_pair(__FINDER__),
            'WKSELECTED': curses.color_pair(__WKS_SELECTED__),
            'CMDLINE': curses.color_pair(__CMDLINE__) | curses.A_BOLD,
            'CMDLINESEPARATOR': curses.color_pair(__CMDLINE_SEPARATOR__),
            'CMDLINEOPTION': curses.color_pair(__CMDLINE_OPTION__),
            'CMDLINEMACRO': curses.color_pair(__CMDLINE_MACRO__),
            'CMDLINEPROGRAM': curses.color_pair(__CMDLINE_PROGRAM__) | curses.A_BOLD,
            'CMDLINENOPROGRAM': curses.color_pair(__CMDLINE_NO_PROGRAM__),
            'CMDLINEPYFUNCTION': curses.color_pair(__CMDLINE_PY_FUNCTION__) | curses.A_BOLD,
            })

