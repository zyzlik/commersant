# -*- encoding: utf8 -*-

import curses


class Menu(object):

    def __init__(self, items, parent, begin_y=None, begin_x=None):
        # items should be tuple of tuples: title, price and function
        self.items = items
        self.parent = parent
        self.panel = None
        self.max_len = max(len(i[0]) + len(str(i[1])) for i in items)
        self.width = self.max_len * 2 + 10
        if not begin_y:
            begin_y = 1
        if not begin_x:
            begin_x = parent.width / 2 - self.width / 2
        self.begin_y = begin_y
        self.begin_x = begin_x

    def draw(self):
        # TODO: finish method
        if not self.panel:
            self.panel = curses.newwin(len(self.items), self.width, self.begin_y, self.begin_x)
