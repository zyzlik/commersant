# -*- encoding: utf8 -*-

import curses


# Constants format: FOREGROUND_BACKGROUND

BLACK_BLUE = 1
BLACK_WHITE = 2
RED_WHITE = 3
WHITE_BLUE = 4
CYAN_BLUE = 5
MAGENTA_BLUE = 6
YELLOW_BLUE = 7
BLACK_CYAN = 8


def init_colors():
    curses.init_pair(BLACK_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(BLACK_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(RED_WHITE, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(WHITE_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(CYAN_BLUE, curses.COLOR_CYAN, curses.COLOR_BLUE)
    curses.init_pair(MAGENTA_BLUE, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
    curses.init_pair(YELLOW_BLUE, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(BLACK_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
