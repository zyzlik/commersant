# -*- encoding: utf8 -*-

from constants import *


class Menu(object):
    bg_color = curses.COLOR_BLACK
    fg_color = curses.COLOR_WHITE
    highlighted_bg_color = curses.COLOR_WHITE
    highlighted_fg_color = curses.COLOR_BLACK
    deactivate_key = curses.KEY_RIGHT
    exit_key = KEY_ESC

    def __init__(self, items, screen, begin_y, begin_x, active=True):
        self.items = items
        self.width = None
        self.height = None
        self.active = active
        if not self.active:
            self.pos = None
        else:
            self.pos = 0
        self.panel = None
        self.screen = screen
        self.begin_y = begin_y
        self.begin_x = begin_x
        curses.init_pair(1, self.fg_color, self.bg_color)
        curses.init_pair(2, self.highlighted_fg_color, self.highlighted_bg_color)

    def _count_width(self):
        self.width = max(len(i) for i in self.items) + 2

    def _count_height(self):
        self.height = len(self.items)

    def _item_up(self):
        if self.pos > 0:
            self.pos -= 1

    def _item_down(self):
        if self.pos < len(self.items) - 1:
            self.pos += 1

    def draw(self):
        self.panel.clear()
        for i, text in enumerate(self.items):
            if i == self.pos and self.active:
                color = 2
            else:
                color = 1
            self.panel.addstr(i, 0, text, curses.color_pair(color))
        self.panel.refresh()

    def attach(self):
        self._count_height()
        self._count_width()
        self.panel = self.screen.derwin(self.height, self.width, self.begin_y, self.begin_x)
        self.panel.keypad(1)
        self.draw()
        self.screen.refresh()

    def wait_for_key(self):
        key = None
        while key != curses.KEY_ENTER and key != KEY_ENTER:
            key = self.panel.getch()
            if key == curses.KEY_UP and self.active:
                self._item_up()
                self.draw()
            elif key == curses.KEY_DOWN and self.active:
                self._item_down()
                self.draw()
            elif key == self.deactivate_key and self.active:
                self.deactivate()
                self.draw()
                return
            elif key == self.exit_key:
                self.deactivate()
                self.draw()
                return -1
        return self.pos

    def activate(self):
        self.active = True
        self.pos = 0

    def deactivate(self):
        self.active = False
        self.pos = None


class MultipleMenu(object):
    active_menu = 0

    def __init__(self, menus):
        self.menus = menus
        self.draw()

    def draw(self):
        for menu in self.menus:
            menu.attach()

    def start(self):
        res = None
        while res is None:
            self.menus[self.active_menu].activate()
            self.draw()
            res = self.menus[self.active_menu].wait_for_key()
            if res is None:
                index = (self.active_menu + 1) % len(self.menus)
                self.active_menu = index
        return res, self.menus[self.active_menu]


def _main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    stdscr.addstr(0, width // 2 - 3, 'Hello')
    items = ('Борщ     10', 'Солянка   15')
    items2 = ('Носок     10', 'Шапка   15')
    menu1 = Menu(items, stdscr, height // 2, width // 2 - 20)
    menu2 = Menu(items2, stdscr, height // 2, width // 2 + 10, active=False)
    menus = MultipleMenu((menu1, menu2))
    res, menu = menus.start()
    if res == -1:
        stdscr.addstr(0, 0, 'Вышли с концами!')
    elif res is not None:
        stdscr.addstr(0, 0, 'Вы выбрали %s' % menu.items[res])
    else:
        stdscr.addstr(0, 0, 'Меню не активно')
    stdscr.refresh()
    stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(_main)
