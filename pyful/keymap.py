# keymap.py - keymap constants of curses
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
KEY_DC = curses.KEY_DC
KEY_NPAGE = curses.KEY_NPAGE
KEY_PPAGE = curses.KEY_PPAGE
KEY_F1 = curses.KEY_F1
KEY_F2 = curses.KEY_F2
KEY_F3 = curses.KEY_F3
KEY_F4 = curses.KEY_F4
KEY_F5 = curses.KEY_F5
KEY_F6 = curses.KEY_F6
KEY_F7 = curses.KEY_F7
KEY_F8 = curses.KEY_F8
KEY_F9 = curses.KEY_F9
KEY_F10 = curses.KEY_F10
KEY_F11 = curses.KEY_F11
KEY_F12 = curses.KEY_F12

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

keyhelp = {
    KEY_CTRL_A: 'Control + a',
    KEY_CTRL_B: 'Control + b',
    KEY_CTRL_C: 'Control + c',
    KEY_CTRL_D: 'Control + d',
    KEY_CTRL_E: 'Control + e',
    KEY_CTRL_F: 'Control + f',
    KEY_CTRL_G: 'Control + g',
    KEY_CTRL_H: 'Control + h',
    KEY_CTRL_I: 'Control + i',
    KEY_CTRL_J: 'Control + j',
    KEY_CTRL_K: 'Control + k',
    KEY_CTRL_L: 'Control + l',
    KEY_CTRL_M: 'Control + m',
    KEY_CTRL_N: 'Control + n',
    KEY_CTRL_O: 'Control + o',
    KEY_CTRL_P: 'Control + p',
    KEY_CTRL_Q: 'Control + q',
    KEY_CTRL_R: 'Control + r',
    KEY_CTRL_S: 'Control + s',
    KEY_CTRL_T: 'Control + t',
    KEY_CTRL_U: 'Control + u',
    KEY_CTRL_V: 'Control + v',
    KEY_CTRL_W: 'Control + w',
    KEY_CTRL_X: 'Control + x',
    KEY_CTRL_Y: 'Control + y',
    KEY_CTRL_Z: 'Control + z',
    KEY_RETURN: 'Return',
    KEY_ESCAPE: 'Escape',
    KEY_SPACE: 'Space',
    KEY_DOWN: 'Down',
    KEY_UP: 'Up',
    KEY_RIGHT: 'Right',
    KEY_LEFT: 'Left',
    KEY_BACKSPACE: 'Backspace',
    KEY_HOME: 'Home',
    KEY_END: 'End',
    KEY_DC: 'Delete',
    KEY_NPAGE: 'PageDown',
    KEY_PPAGE: 'PageUp',
    KEY_F1: 'F1',
    KEY_F2: 'F2',
    KEY_F3: 'F3',
    KEY_F4: 'F4',
    KEY_F5: 'F5',
    KEY_F6: 'F6',
    KEY_F7: 'F7',
    KEY_F8: 'F8',
    KEY_F9: 'F9',
    KEY_F10: 'F10',
    KEY_F11: 'F11',
    KEY_F12: 'F12',
    KEY_0: '0',
    KEY_1: '1',
    KEY_2: '2',
    KEY_3: '3',
    KEY_4: '4',
    KEY_5: '5',
    KEY_6: '6',
    KEY_7: '7',
    KEY_8: '8',
    KEY_9: '9',
    KEY_a: 'a',
    KEY_b: 'b',
    KEY_c: 'c',
    KEY_d: 'd',
    KEY_e: 'e',
    KEY_f: 'f',
    KEY_g: 'g',
    KEY_h: 'h',
    KEY_i: 'i',
    KEY_j: 'j',
    KEY_k: 'k',
    KEY_l: 'l',
    KEY_m: 'm',
    KEY_n: 'n',
    KEY_o: 'o',
    KEY_p: 'p',
    KEY_q: 'q',
    KEY_r: 'r',
    KEY_s: 's',
    KEY_t: 't',
    KEY_u: 'u',
    KEY_v: 'v',
    KEY_w: 'w',
    KEY_x: 'x',
    KEY_y: 'y',
    KEY_z: 'z',
    KEY_A: 'Shift + a',
    KEY_B: 'Shift + b',
    KEY_C: 'Shift + c',
    KEY_D: 'Shift + d',
    KEY_E: 'Shift + e',
    KEY_F: 'Shift + f',
    KEY_G: 'Shift + g',
    KEY_H: 'Shift + h',
    KEY_I: 'Shift + i',
    KEY_J: 'Shift + j',
    KEY_K: 'Shift + k',
    KEY_L: 'Shift + l',
    KEY_M: 'Shift + m',
    KEY_N: 'Shift + n',
    KEY_O: 'Shift + o',
    KEY_P: 'Shift + p',
    KEY_Q: 'Shift + q',
    KEY_R: 'Shift + r',
    KEY_S: 'Shift + s',
    KEY_T: 'Shift + t',
    KEY_U: 'Shift + u',
    KEY_V: 'Shift + v',
    KEY_W: 'Shift + w',
    KEY_X: 'Shift + x',
    KEY_Y: 'Shift + y',
    KEY_Z: 'Shift + z',
    KEY_EXCLAM: '!',
    KEY_DQUOTE: '"',
    KEY_SHARP: '#',
    KEY_DOLLAR: '$',
    KEY_PERCENT: '%',
    KEY_AND: '&',
    KEY_SQUOTE: '\'',
    KEY_LPAREN: '(',
    KEY_RPAREN: ')',
    KEY_TILDA: '~',
    KEY_EQUAL: '=',
    KEY_MINUS: '-',
    KEY_CUP: '^',
    KEY_VBAR: '|',
    KEY_BSLASH: '\\',
    KEY_ATMARK: '@',
    KEY_BQUOTE: '`',
    KEY_LCURLY: '{',
    KEY_LBRACK: '[',
    KEY_PLUS: '+',
    KEY_SCOLON: ';',
    KEY_STAR: '*',
    KEY_COLON: ':',
    KEY_RCURLY: '}',
    KEY_RBRACK: ']',
    KEY_LSS: '<',
    KEY_COMMA: ',',
    KEY_GTR: '>',
    KEY_DOT: '.',
    KEY_SLASH: '/',
    KEY_QMARK: '?',
    KEY_USCORE: '_',
    }
