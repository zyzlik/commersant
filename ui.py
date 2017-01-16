# -*- encoding: utf8 -*-

import curses
import random
import time

from collections import OrderedDict
from datetime import date, timedelta

from observer import Observable, Observer
from utils import human_money


"""
class Menu
class Bank
class Exchange
"""

DATE = date(2017, 1, 1)
TIMEDELTA = timedelta(days=1)

YES = 1
NO = 0

INITIAL_LOAN_RATE = 10
INITIAL_DEPOSIT_RATE = 8
RATE_SCATTER = (5, 15)
INITIAL_INCOME_TAX = 5
INITIAL_REPLACEMENT_COST = 19

KEY_0 = 48
KEY_1 = 49


class Bank(Observer):

    def __init__(self):
        self.loan_rate = INITIAL_LOAN_RATE
        self.deposit_rate = INITIAL_DEPOSIT_RATE

    def update(self, date):
        if date.day == 1:
            self.loan_rate = random.randint(*RATE_SCATTER)
            self.deposit_rate = random.randint(*RATE_SCATTER)

    def update_deposits(self, deposits):
        for month, money in deposits.items():
            deposits[month] = money + money * self.deposit_rate / 100

    def update_loans(self, loans):
        for month, money in loans.items():
            loans[month] = money + money * self.loan_rate / 100


class User(Observer):

    def __init__(self, name):
        self.name = name
        self.scores = 0
        self.total_money = 30000
        self.property = {
            'apt': None,
            'car': None,
            'oil': None,
            'land': None,
        }
        self.marriage = False
        self.sick = False
        self.deposits = {
            1: 10000,
            5: 15500
        }
        self.loans = {
            6: 12200
        }
        self.bank = Bank()
        self.month = None

    def update(self, date):
        self.month = date.month
        if date.day == 1:
            if date.month in self.deposits:
                self.get_payment(date.month)
            if date.month in self.loans:
                self.pay_loan(date.month)
            self.bank.update_deposits(self.deposits)
            self.bank.update_loans(self.loans)

    def get_payment(self, month):
        self.total_money += self.deposits.pop(month)

    def pay_loan(self, month):
        self.total_money -= self.loans.pop(month)

    def new_deposit(self, amount, term):
        if amount < self.total_money:
            month = (self.month + term) % 12
            self.deposits.update({month: amount})
            self.total_money -= amount
            return True
        else:
            return False

    def new_loan(self, amount, term):
        if amount < self.total_money:
            month = (self.month + term) % 12
            self.loans.update({month: amount})
            self.total_money += amount
            return True
        else:
            return False


class DateCounter(Observable):
    pass


class Screen(object):

    def __init__(self):
        self.screen = curses.initscr()
        self.screen.nodelay(YES)
        self.screen.immedok(True)
        self.screen.keypad(True)
        self.height, self.width = self.screen.getmaxyx()
        self.padding = 2
        self.side_panel_width = self.width // 2 - 2 * self.padding

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.def_prog_mode()

        self.screen.bkgd(' ', curses.color_pair(1))
        self.user = User('Ksenia')
        self.menu = MenuPanel(self)
        self.date = DatePanel(self.side_panel_width)
        self.tax = TaxPanel(self.side_panel_width)
        self.finance = FinancePanel(self.width, self.user)
        self.bank = BankPanel(self.width, self.height, self.user)

        self.options = {
            curses.KEY_F1: self.show_bank,
            curses.KEY_F2: self.show_market,
            curses.KEY_F3: self.show_exchange,
            # curses.KEY_F4: self.show_property,
            # curses.KEY_F9: self.show_secretary,
        }

    def draw_event_window(self):
        wind = curses.newwin(3, self.width // 2, self.height // 2, self.width // 4)
        wind.border(1)
        wind.bkgd(' ', curses.color_pair(1))
        return wind

    def show_bank(self):
        self.bank.draw()

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


class MenuPanel(object):

    def __init__(self, main, options=None):
        self.options = options
        if self.options is None:
            self.options = OrderedDict([
                ('F1', 'Банк'),
                ('F2', 'Рынок'),
                ('F3', 'Биржа'),
                ('F4', 'Хозяйство'),
                ('F9', 'Секретарь'),
                ('ESC', 'Выход'),
            ])
        self.main = main
        self.draw()

    def draw(self):
        count_len = 0
        for key in self.options:
            count_len += len(key) + 1 + len(self.options[key]) + 1
        menu = curses.newwin(1, count_len + 4, self.main.height - 1, self.main.width // 2 - count_len // 2)
        menu.bkgd(' ', curses.color_pair(2))
        y = 0
        x = 2
        for key in self.options:
            s = '%s' % (key)
            menu.addstr(y, x, s, curses.color_pair(3))
            x += len(s)
            s = ':%s ' % (self.options[key])
            menu.addstr(y, x, s)
            x += len(s)
        menu.refresh()


class DatePanel(Observer):

    def __init__(self, width):
        self.date = DATE
        self.panel = curses.newwin(4, width, 2, 2)
        self.draw()

    def draw(self):
        self.panel.clear()
        date_str = 'Сегодня: %s' % self.date.strftime('%d-%b-%Y')
        weekday_str = self.date.strftime('%A')
        height, width = self.panel.getmaxyx()
        self.panel.bkgd(' ', curses.color_pair(4))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.addstr(1, width // 2 - len(date_str) // 2, date_str)
        self.panel.addstr(2, width // 2 - len(weekday_str) // 2, weekday_str)
        self.panel.refresh()

    def update(self, date):
        self.date = date
        self.draw()


class TaxPanel(Observer):

    def __init__(self, width):
        self.loan_rate = INITIAL_LOAN_RATE
        self.deposit_rate = INITIAL_DEPOSIT_RATE
        self.income_tax = INITIAL_INCOME_TAX
        self.replacement_cost = INITIAL_REPLACEMENT_COST
        self.panel = curses.newwin(6, width, 7, 2)
        self.draw()

    def draw(self):
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(4))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        loan_rate_str = 'Процент под кредит: %s' % self.loan_rate
        deposit_rate_str = 'Процент под долг: %s' % self.deposit_rate
        income_tax_str = 'Подоходный налог: %s' % self.income_tax
        replacement_cost_str = 'ВС: %s' % self.replacement_cost
        self.panel.addstr(1, 2, loan_rate_str)
        self.panel.addstr(2, 2, deposit_rate_str)
        self.panel.addstr(3, 2, income_tax_str)
        self.panel.addstr(4, 2, replacement_cost_str)
        self.panel.refresh()

    def update(self, date):
        if date.day == 1:
            self.draw()


class FinancePanel(Observer):

    def __init__(self, main_width, user):
        self.user = user
        self.panel = curses.newwin(9, main_width // 2 - 1, 2, main_width // 2)
        self.month_income = 0
        self.house_rate = 15
        self.land_rate = 10
        self.draw()

    def draw(self):
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(4))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        height, width = self.panel.getmaxyx()
        money_str = 'У вас на счету: %s %s' % (self.user.total_money, human_money(self.user.total_money))
        deposit_str = 'Вам должны: %s %s' % (sum(self.user.deposits.values()), human_money(sum(self.user.deposits.values())))
        loan_str = 'Вы должны: %s %s' % (sum(self.user.loans.values()), human_money(sum(self.user.loans.values())))
        month_income_str = 'Итого прибыль: %s %s' % (self.month_income, human_money(self.month_income))
        house_rate_str = 'Плата за дом: %s%%' % self.house_rate
        land_rate_str = 'Плата за землю: %s%%' % self.land_rate
        self.panel.addstr(1, 2, money_str)
        self.panel.addstr(2, 2, deposit_str)
        self.panel.addstr(3, 2, loan_str)
        self.panel.addstr(4, 2, month_income_str)
        self.panel.addstr(5, 2, '_' * (width - 4))
        self.panel.addstr(6, 2, house_rate_str)
        self.panel.addstr(7, 2, land_rate_str)
        self.panel.refresh()

    def update(self, date):
        self.draw()


class BankPanel(object):

    def __init__(self, main_width, main_height, user):
        self.panel = curses.newwin(main_height // 2, main_width - 8, main_height // 2 - 4, 4)
        self.user = user

    def draw(self):
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(1))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        height, width = self.panel.getmaxyx()
        bank_name = ' Банк Ivanov & Co. '
        self.panel.addstr(0, width // 2 - len(bank_name) // 2, bank_name)
        self.panel.addstr(2, 1, '+')
        self.panel.addstr(3, 1, '+')
        self.panel.addstr(4, 1, '-')
        self.panel.addstr(5, 1, '-')
        m = 1
        for i in range(5, width, width // 6):
            self.panel.addstr(1, i, str(m))

            def row(month, plus=True):
                if plus:
                    if month <= 6:
                        return 2
                    return 3
                else:
                    if month <= 6:
                        return 4
                    return 5

            if m in self.user.deposits or m + 6 in self.user.deposits:
                for month, money in self.user.deposits.items():
                    if month % 6 == m:
                        self.panel.addstr(row(month), i, str(money))
                    elif month % 6 == 0 and m == 6:
                        self.panel.addstr(row(month), i, str(money))
            else:
                self.panel.addstr(2, i, str(0))
                self.panel.addstr(3, i, str(0))

            if m in self.user.loans or m + 6 in self.user.loans:
                for month, money in self.user.loans.items():
                    if month % 6 == m:
                        self.panel.addstr(row(month, False), i, str(money))
                    elif month % 6 == 0 and m == 6:
                        self.panel.addstr(row(month, False), i, str(money))
            else:
                self.panel.addstr(4, i, str(0))
                self.panel.addstr(5, i, str(0))
            m += 1
        self.panel.addstr(6, 2, '_' * (width - 4))
        self.panel.refresh()
        self.panel.nodelay(NO)
        key = self.panel.getch()
        if key:
            self.draw_choice()

    def draw_choice(self):
        height, width = self.panel.getmaxyx()
        title = 'Вы хотите'
        question = 'взять [1] или дать [0] деньги под проценты?'
        choice_panel = self.panel.derwin(5, len(question) + 2, height // 2, width // 2 - len(question) // 2)
        choice_panel.clear()
        choice_panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        height, width = choice_panel.getmaxyx()
        choice_panel.addstr(0, width // 2 - len(title) // 2, title)
        choice_panel.addstr(2, width // 2 - len(question) // 2, question)
        self.panel.refresh()
        choice_panel.refresh()
        choice_panel.nodelay(NO)
        key = choice_panel.getch()
        if key == KEY_0:
            choice_panel.erase()
            del choice_panel
            self.panel.refresh()
            self.panel.addstr(7, 2, 'Какую сумму вы хотели бы дать? ')
            curses.echo()
            amount = self.panel.getstr()
            if self.validate_int(amount):
                self.panel.addstr(8, 2, 'На какой срок (1-11 месяцев)? ')
                curses.echo()
                term = self.panel.getstr()
                if self.validate_int(term) and self.validate_month(term):
                    self.user.new_deposit(int(amount), int(term))
            self.hide()
        if key == KEY_1:
            del choice_panel
            self.panel.addstr(7, 2, 'Какую сумму вы хотели бы взять?')

    def hide(self):
        self.panel.erase()
        self.panel.refresh()
        del self.panel

    def validate_int(self, input):
        if input.isdigit():
            return True
        return False

    def validate_month(self, input):
        if 11 >= int(input) >= 1:
            return True
        else:
            return False


if __name__ == '__main__':
    date_counter = DateCounter()
    current_date = DATE
    screen = Screen()
    date_counter.register(screen.date)
    date_counter.register(screen.tax)
    date_counter.register(screen.user)
    date_counter.register(screen.user.bank)
    date_counter.register(screen.finance)
    count = 10
    while count != 0:
        time.sleep(1)
        current_date = current_date + TIMEDELTA
        date_counter.notify(current_date)
        key = screen.screen.getch()
        if key in screen.options:
            screen.options[key]()
        elif key == 27:
            count = 0
        else:
            count -= 1
    curses.endwin()
