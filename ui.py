# -*- encoding: utf8 -*-

import curses
import time

from collections import OrderedDict

"""
class Menu
class Bank
class Exchange
"""


s = 'I \u2764 Oleg'
heart = '\u2764'


class Screen(object):

    def __init__(self):
        self.menu = Menu()
        self.screen = curses.initscr()
        self.screen.immedok(True)
        self.screen.keypad(True)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.def_prog_mode()

        self.height, self.width = self.screen.getmaxyx()
        self.draw_main()
        self.draw_menu()

        self.listen_events()
        curses.endwin()

    def listen_events(self):
        options = {
            curses.KEY_F1: self.show_bank,
            curses.KEY_F2: self.show_market,
            curses.KEY_F3: self.show_exchange,
            # curses.KEY_F4: self.show_property,
            # curses.KEY_F9: self.show_secretary,
            # curses.KEY_EXIT: curses.endwin,
        }

        key = self.screen.getch()
        if key in options:
            options[key]()

    def draw_event_window(self):
        wind = curses.newwin(3, self.width // 2, self.height // 2, self.width // 4)
        wind.border(1)
        wind.bkgd(' ', curses.color_pair(1))
        return wind

    def show_bank(self):
        wind = self.draw_event_window()
        height, width = wind.getmaxyx()
        s = 'Вы попали в банк'
        wind.addstr(height // 2, width // 2 - len(s) // 2, s)
        wind.refresh()
        time.sleep(2)

    def show_market(self):
        wind = self.draw_event_window()
        height, width = wind.getmaxyx()
        s = 'Вы попали на рынок'
        wind.addstr(height // 2, width // 2 - len(s) // 2, s)
        wind.refresh()
        time.sleep(2)

    def show_exchange(self):
        wind = self.draw_event_window()
        height, width = wind.getmaxyx()
        s = 'Вы попали на биржу'
        wind.addstr(height // 2, width // 2 - len(s) // 2, s)
        wind.refresh()
        time.sleep(2)

    def draw_main(self):
        self.screen.border(0)
        self.screen.bkgd(' ', curses.color_pair(1))

    def draw_menu(self):
        menu = curses.newwin(2, self.width-4, self.height - 2, 2)
        menu.bkgd(' ', curses.color_pair(2))
        y = 0
        x = 0
        for opt in self.menu.options:
            key = '%s' % (opt)
            name = '-%s' % (self.menu.options[opt])
            menu.addstr(y, x, key, curses.color_pair(3))
            menu.addstr(y, x + len(key), name)
            x += len(key) + len(name) + 1
        menu.refresh()


class Menu(object):

    def __init__(self):
        self.options = OrderedDict([
            ('F1', 'Банк'),
            ('F2', 'Рынок'),
            ('F3', 'Биржа'),
            ('F4', 'Хозяйство'),
            ('F9', 'Секретарь'),
            ('ESC', 'Выход'),
        ])


if __name__ == '__main__':
    Screen()


