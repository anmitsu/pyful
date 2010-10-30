# keymap.py - keymap constants of curses
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

import curses

META = True
NONE = False

KEY_CTRL_A = 1
KEY_CTRL_B = 2
KEY_CTRL_C = 3
KEY_CTRL_D = 4
KEY_CTRL_E = 5
KEY_CTRL_F = 6
KEY_CTRL_G = 7
KEY_CTRL_H = 8
KEY_CTRL_I = 9
KEY_CTRL_J = 10
KEY_CTRL_K = 11
KEY_CTRL_L = 12
KEY_CTRL_M = 10
KEY_CTRL_N = 14
KEY_CTRL_O = 15
KEY_CTRL_P = 16
KEY_CTRL_Q = 17
KEY_CTRL_R = 18
KEY_CTRL_S = 19
KEY_CTRL_T = 20
KEY_CTRL_U = 21
KEY_CTRL_V = 22
KEY_CTRL_W = 23
KEY_CTRL_X = 24
KEY_CTRL_Y = 25
KEY_CTRL_Z = 26

KEY_RETURN = 10
KEY_ESCAPE = 27
KEY_SPACE = 32

KEY_DOWN = curses.KEY_DOWN
KEY_UP = curses.KEY_UP
KEY_RIGHT = curses.KEY_RIGHT
KEY_LEFT = curses.KEY_LEFT
KEY_BACKSPACE = curses.KEY_BACKSPACE
KEY_HOME = curses.KEY_HOME
KEY_END = curses.KEY_END

KEY_0 = ord("0")
KEY_1 = ord("1")
KEY_2 = ord("2")
KEY_3 = ord("3")
KEY_4 = ord("4")
KEY_5 = ord("5")
KEY_6 = ord("6")
KEY_7 = ord("7")
KEY_8 = ord("8")
KEY_9 = ord("9")

KEY_a = ord("a")
KEY_b = ord("b")
KEY_c = ord("c")
KEY_d = ord("d")
KEY_e = ord("e")
KEY_f = ord("f")
KEY_g = ord("g")
KEY_h = ord("h")
KEY_i = ord("i")
KEY_j = ord("j")
KEY_k = ord("k")
KEY_l = ord("l")
KEY_m = ord("m")
KEY_n = ord("n")
KEY_o = ord("o")
KEY_p = ord("p")
KEY_q = ord("q")
KEY_r = ord("r")
KEY_s = ord("s")
KEY_t = ord("t")
KEY_u = ord("u")
KEY_v = ord("v")
KEY_w = ord("w")
KEY_x = ord("x")
KEY_y = ord("y")
KEY_z = ord("z")

KEY_A = ord("A")
KEY_B = ord("B")
KEY_C = ord("C")
KEY_D = ord("D")
KEY_E = ord("E")
KEY_F = ord("F")
KEY_G = ord("G")
KEY_H = ord("H")
KEY_I = ord("I")
KEY_J = ord("J")
KEY_K = ord("K")
KEY_L = ord("L")
KEY_M = ord("M")
KEY_N = ord("N")
KEY_O = ord("O")
KEY_P = ord("P")
KEY_Q = ord("Q")
KEY_R = ord("R")
KEY_S = ord("S")
KEY_T = ord("T")
KEY_U = ord("U")
KEY_V = ord("V")
KEY_W = ord("W")
KEY_X = ord("X")
KEY_Y = ord("Y")
KEY_Z = ord("Z")

KEY_EXCLAM  = ord("!")
KEY_DQUOTE  = ord("\"")
KEY_SHARP   = ord("#")
KEY_DOLLAR  = ord("$")
KEY_PERCENT = ord("%")
KEY_AND     = ord("&")
KEY_SQUOTE  = ord("'")
KEY_LPAREN  = ord("(")
KEY_RPAREN  = ord(")")
KEY_TILDA   = ord("~")
KEY_EQUAL   = ord("=")
KEY_MINUS   = ord("-")
KEY_CUP     = ord("^")
KEY_VBAR    = ord("|")
KEY_BSLASH  = ord("\\")
KEY_ATMARK  = ord("@")
KEY_BQUOTE  = ord("`")
KEY_LCURLY  = ord("{")
KEY_LBRACK  = ord("[")
KEY_PLUS    = ord("+")
KEY_SCOLON  = ord(";")
KEY_STAR    = ord("*")
KEY_COLON   = ord(":")
KEY_RCURLY  = ord("}")
KEY_RBRACK  = ord("]")
KEY_LSS     = ord("<")
KEY_COMMA   = ord(",")
KEY_GTR     = ord(">")
KEY_DOT     = ord(".")
KEY_SLASH   = ord("/")
KEY_QMARK   = ord("?")
KEY_USCORE  = ord("_")
