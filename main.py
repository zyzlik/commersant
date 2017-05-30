# -*- encoding: utf8 -*-

import curses
import random
import time

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from datetime import date, timedelta

from observer import Observable, Observer
from utils import human_money, construct_date


DATE = date(2017, 1, 1)
TIMEDELTA = timedelta(days=1)

YES = 1
NO = 0

INITIAL_LOAN_RATE = 10
INITIAL_DEPOSIT_RATE = 8
RATE_SCATTER = (5, 15)
INITIAL_INCOME_TAX = 5
INITIAL_REPLACEMENT_COST = 19

INITIAL_INCOME = 0
INITIAL_LAND_RATE = 10
INITIAL_HOUSE_RATE = 10

KEY_0 = 48
KEY_1 = 49
KEY_ESC = 27

MENU_OPTIONS = OrderedDict([
    ('F1', 'Банк'),
    ('F2', 'Рынок'),
    ('F3', 'Биржа'),
    ('F4', 'Хозяйство'),
    ('F9', 'Секретарь'),
    ('ESC', 'Выход'),
])


class Panel(metaclass=ABCMeta):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        self.panel = None
        self.parent = parent
        self.height = height
        self.width = width
        self.begin_y = begin_y
        self.begin_x = begin_x

    @abstractmethod
    def add_content(self):
        pass

    def create_panel(self):
        if not self.panel:
            self.panel = curses.newwin(self.height, self.width, self.begin_y, self.begin_x)
        return self.panel

    def show(self):
        if not self.panel:
            self.create_panel()
        self.add_content()
        self.panel.refresh()
        return self.panel

    def hide(self):
        self.parent.panel.touchwin()
        self.parent.panel.refresh()
        self.panel = None


class DateCounter(Observable):
    pass


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


class Market(Observer):

    def __init__(self):
        self.cars = OrderedDict([
            ('Луаз-969', {'price': 0, 'price_range': (6500, 12000)}),
            ('Москвич-412', {'price': 0, 'price_range': (10000, 20000)}),
            ('Москвич-2141', {'price': 0, 'price_range': (18000, 27000)}),
            ('ВАЗ-2106', {'price': 0, 'price_range': (24000, 37000)}),
            ('ВАЗ-2109', {'price': 0, 'price_range': (33000, 50000)}),
            ('ГАЗ-24', {'price': 0, 'price_range': (45000, 65000)}),
            ('ГАЗ-3102', {'price': 0, 'price_range': (60000, 75000)}),
        ])
        self.apartments = OrderedDict([
            ('1-комн', {'price': 0, 'price_range': (6500, 12000)}),
            ('2-комн', {'price': 0, 'price_range': (9000, 17000)}),
            ('3-комн', {'price': 0, 'price_range': (16000, 30000)}),
            ('4-комн', {'price': 0, 'price_range': (20000, 35000)}),
            ('5-комн', {'price': 0, 'price_range': (27000, 50000)}),
            ('6-комн', {'price': 0, 'price_range': (35000, 65000)}),
            ('7-комн', {'price': 0, 'price_range': (40000, 75000)}),
        ])
        self.update_apartments()
        self.update_cars()

    def update(self, date):
        if date.day == 1:
            self.update_cars()
            self.update_apartments()

    def update_cars(self):
        for car in self.cars:
            self.cars[car]['price'] = random.randrange(*self.cars[car]['price_range'])

    def update_apartments(self):
        for apt in self.apartments:
            self.apartments[apt]['price'] = random.randrange(*self.apartments[apt]['price_range'])


class User(Observer):

    def __init__(self, name):
        self.name = name
        self.scores = 0
        self.total_money = 30000
        self.property = {
            'apt': 'Живу у мамы',
            'car': None,
            'oil': None,
            'land': None,
        }
        self.marriage = False
        self.sick = False
        self.deposits = {construct_date(day=4): 10000}
        self.loans = {}
        self.bank = Bank()
        self.market = Market()
        self.date = None

    def update(self, date):
        # If day is the day of your deposit, it is time to adjust percents
        for d in self.deposits:
            if d.day == date.day:
                self.bank.update_deposits(self.deposits)
        for d in self.loans:
            if d.day == date.day:
                self.bank.update_loans(self.loans)
        # If it is a day of payment, make payments
        self.date = date
        if date in self.deposits:
            self.get_payment(date)
        if date in self.loans:
            self.pay_loan(date)

    def get_payment(self, date):
        self.total_money += self.deposits.pop(date)

    def pay_loan(self, date):
        self.total_money -= self.loans.pop(date)

    def new_deposit(self, amount, term):
        if amount < self.total_money:
            month = (self.date.month + term) % 12
            if month < self.date.month:
                year = self.date.year + 1
            else:
                year = self.date.year
            return_date = construct_date(self.date.day, month, year)
            self.deposits.update({return_date: amount})
            self.total_money -= amount
            return True
        else:
            return False

    def new_loan(self, amount, term):
        if amount < self.total_money:
            month = (self.date.month + term) % 12
            if month < self.date.month:
                year = self.date.year + 1
            else:
                year = self.date.year
            return_date = construct_date(self.date.day, month, year)
            self.loans.update({return_date: amount})
            self.total_money += amount
            return True
        else:
            return False

    def get_month_deposits(self, month):
        amount = 0
        for deposit, money in self.deposits.items():
            if deposit.month == month:
                amount += money
        return amount

    def get_month_loans(self, month):
        amount = 0
        for loan, money in self.loans.items():
            if loan.month == month:
                amount += money
        return amount

    def buy_car(self, car):
        price = self.market.cars[car]['price']
        if price < self.total_money:
            self.total_money -= price
            self.property['car'] = car
            return True
        return False

    def buy_apartment(self, apt):
        price = self.market.apartments[apt]['price']
        if price < self.total_money:
            self.total_money -= price
            self.property['apt'] = apt
            return True
        return False


class MenuPanel(Panel):

    def _count_width(self):
        count_len = 0
        for key in self.options:
            count_len += len(key) + 1 + len(self.options[key]) + 1
        return count_len

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(MenuPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.options = kwargs.get('options')
        if self.options is None:
            self.options = MENU_OPTIONS
        self.width = self._count_width() + 4
        self.begin_x = parent.width // 2 - self.width // 2

    def add_content(self):
        if not self.panel:
            self.create_panel()
        count_len = 0
        for key in self.options:
            count_len += len(key) + 1 + len(self.options[key]) + 1
        self.panel.bkgd(' ', curses.color_pair(2))
        y = 0
        x = 2
        for key in self.options:
            s = '%s' % (key)
            self.panel.addstr(y, x, s, curses.color_pair(3))
            x += len(s)
            s = ':%s ' % (self.options[key])
            self.panel.addstr(y, x, s)
            x += len(s)


class TaxPanel(Observer, Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(TaxPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.loan_rate = INITIAL_LOAN_RATE
        self.deposit_rate = INITIAL_DEPOSIT_RATE
        self.income_tax = INITIAL_INCOME_TAX
        self.replacement_cost = INITIAL_REPLACEMENT_COST

    def add_content(self):
        if not self.panel:
            self.create_panel()
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
            self.show()


class FinancePanel(Observer, Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(FinancePanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.month_income = INITIAL_INCOME
        self.house_rate = INITIAL_HOUSE_RATE
        self.land_rate = INITIAL_LAND_RATE

    def add_content(self):
        if not self.panel:
            self.create_panel()
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(4))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        height, width = self.panel.getmaxyx()
        money_str = 'У вас на счету: %s %s' % (
            self.user.total_money, human_money(self.user.total_money))
        deposit_str = 'Вам должны: %s %s' % (
            sum(self.user.deposits.values()), human_money(sum(self.user.deposits.values())))
        loan_str = 'Вы должны: %s %s' % (
            sum(self.user.loans.values()), human_money(sum(self.user.loans.values())))
        month_income_str = 'Итого прибыль: %s %s' % (
            self.month_income, human_money(self.month_income))
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
        pass


class DatePanel(Observer, Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(DatePanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.date = DATE

    def add_content(self):
        self.panel.clear()
        date_str = 'Сегодня: %s' % self.date.strftime('%d-%b-%Y')
        weekday_str = self.date.strftime('%A')
        self.panel.bkgd(' ', curses.color_pair(4))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.addstr(1, self.width // 2 - len(date_str) // 2, date_str)
        self.panel.addstr(2, self.width // 2 - len(weekday_str) // 2, weekday_str)
        self.panel.refresh()

    def update(self, date):
        self.date = date
        self.show()

    def hide(self):
        self.main.touchwin()
        self.main.refresh()
        del self.panel


class BankPanel(Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(BankPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')

    @staticmethod
    def _row(month, plus=True):
        if plus:
            if month <= 6:
                return 2
            return 3
        else:
            if month <= 6:
                return 4
            return 5

    def add_content(self):
        if not self.panel:
            self.create_panel()
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(5))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        bank_name = ' Банк Ivanov & Co. '
        self.panel.addstr(0, self.width // 2 - len(bank_name) // 2, bank_name)
        self.panel.addstr(2, 1, '+')
        self.panel.addstr(3, 1, '+')
        self.panel.addstr(4, 1, '-')
        self.panel.addstr(5, 1, '-')
        self.add_payments_table()
        self.panel.addstr(6, 2, '_' * (self.width - 4))

    def add_payments_table(self):
        m = 1
        for i in range(5, self.width, self.width // 6):
            self.panel.addstr(1, i - 2, str(m))

            self.panel.addstr(2, i, str(self.user.get_month_deposits(m)))
            self.panel.addstr(3, i, str(self.user.get_month_deposits(m + 6)))

            self.panel.addstr(4, i, str(self.user.get_month_loans(m)))
            self.panel.addstr(5, i, str(self.user.get_month_loans(m + 6)))
            m += 1

    def ask_for_deposit(self):
        self.panel.addstr(7, 2, 'Какую сумму вы хотели бы дать? ')
        self.panel.refresh()
        curses.echo()
        amount = self.panel.getstr()
        if self.validate_int(amount):
            self.panel.addstr(8, 2, 'На какой срок (1-11 месяцев)? ')
            curses.echo()
            term = self.panel.getstr()
            if self.validate_int(term) and self.validate_month(term):
                self.user.new_deposit(int(amount), int(term))
        curses.noecho()

    def ask_for_loan(self):
        self.panel.addstr(7, 2, 'Какую сумму вы хотели бы взять? ')
        self.panel.refresh()
        curses.echo()
        amount = self.panel.getstr()
        if self.validate_int(amount):
            self.panel.addstr(8, 2, 'На какой срок (1-11 месяцев)? ')
            curses.echo()
            term = self.panel.getstr()
            if self.validate_int(term) and self.validate_month(term):
                self.user.new_loan(int(amount), int(term))
        curses.noecho()

    @staticmethod
    def validate_int(inp):
        if inp.isdigit():
            return True
        return False

    @staticmethod
    def validate_month(inp):
        if 11 >= int(inp) >= 1:
            return True
        else:
            return False


class BankChoicePanel(Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(BankChoicePanel, self).__init__(
            parent, height, width, begin_y, begin_x, *args, **kwargs
        )
        self.question = kwargs.get('question')
        self.title = kwargs.get('title')
        self.width = len(self.question) + 2
        self.begin_x = self.parent.width // 2 - len(self.question) // 2

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(6))
        self.panel.addstr(
            0, self.width // 2 - len(self.title) // 2, self.title, curses.color_pair(5)
        )
        self.panel.addstr(
            2, self.width // 2 - len(self.question) // 2, self.question, curses.color_pair(5)
        )


class MarketPanel(Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(MarketPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.title = ' Рынок '
        self.market = Market()
        self.car_pos = 1
        self.apt_pos = 0

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(6))
        self.panel.addstr(
            0, self.width // 2 - len(self.title) // 2, self.title, curses.color_pair(5)
        )
        table_headers = ('А. Автомобили', 'D. Дома')
        self.panel.addstr(
            1, 2, table_headers[0], curses.color_pair(7)
        )
        self.panel.addstr(
            1, self.width - 10 - len(table_headers[1]), table_headers[1], curses.color_pair(7)
        )
        for i, car in enumerate(self.market.cars, 1):
            if i == self.car_pos:
                color = curses.color_pair(8)
            else:
                color = curses.color_pair(5)
            self.panel.addstr(
                2 + i, 2, '%s. %s' % (i, car), color
            )
            self.panel.addstr(
                2 + i, 15, ' - ' + str(self.market.cars[car]['price']), color
            )

        for i, apt in enumerate(self.market.apartments, 1):
            if i == self.car_pos:
                color = curses.color_pair(8)
            else:
                color = curses.color_pair(5)
            self.panel.addstr(
                2 + i, self.width - 18, apt, color
            )
            self.panel.addstr(
                2 + i, self.width - 11, ' - ' + str(self.market.apartments[apt]['price']), color
            )

class Screen(Observer):

    def __init__(self, stdscr):
        self.panel = stdscr
        # Ожидание getch() не останавливает время
        self.panel.nodelay(YES)
        self.height, self.width = self.panel.getmaxyx()

        self.padding = 2
        self.side_panel_width = self.width // 2 - 2 * self.padding

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.panels = []

        self.panel.bkgd(curses.ACS_CKBOARD, curses.color_pair(2))
        self.panel.refresh()

        self.user = User('Ksenia')
        self.menu = MenuPanel(self, 1, 1, self.height - 1, 2)
        self.date = DatePanel(self, 4, self.side_panel_width, 2, 2)
        self.tax = TaxPanel(self, 6, self.side_panel_width, 7, 2)
        self.finance = FinancePanel(
            self, 9, self.width // 2 - 1, 2, self.width // 2, user=self.user
        )
        self.bank = BankPanel(
            self, self.height // 2, self.width - 8, self.height // 2 - 4, 4, user=self.user
        )
        self.market = MarketPanel(
            self, self.height // 2 + 2, self.width - 30, self.height // 2 - 4, 15, user=self.user
        )

        self.panels.append(self.menu)
        self.panels.append(self.date)
        self.panels.append(self.tax)
        self.panels.append(self.finance)

        self.update_panels()

        self.options = {
            curses.KEY_F1: self.show_bank,
            curses.KEY_F2: self.show_market,
            curses.KEY_F3: [self.enable_panel, self.menu],
            # curses.KEY_F4: self.show_property,
            # curses.KEY_F9: self.show_secretary,
        }

    def update(self, msg):
        self.update_panels()

    def disable_panel(self, panel):
        if panel in self.panels:
            self.panels.remove(panel)
            panel.hide()
        self.update_panels()
        self.panel.refresh()

    def enable_panel(self, panel):
        self.panels.append(panel)
        self.update_panels()
        self.panel.refresh()

    def update_panels(self):
        for panel in self.panels:
            panel.show()
        self.panel.refresh()

    def show_bank(self):
        self.enable_panel(self.bank)
        self.panel.nodelay(NO)
        key = self.panel.getch()
        if key:
            title = ' Вы хотите '
            question = 'взять [1] или дать [0] деньги под проценты?'
            choice_panel = BankChoicePanel(
                self, 5, 1, self.height // 2, 1, question=question, title=title
            )
            self.panels.append(choice_panel)
            self.update_panels()
            key = self.panel.getch()
            if key == KEY_0:
                self.disable_panel(choice_panel)
                curses.noecho()
                self.bank.ask_for_deposit()
            elif key == KEY_1:
                self.disable_panel(choice_panel)
                curses.noecho()
                self.bank.ask_for_loan()
            else:
                curses.noecho()
                self.disable_panel(choice_panel)
        self.panel.nodelay(YES)
        self.disable_panel(self.bank)

    def show_market(self):
        self.enable_panel(self.market)
        self.panel.nodelay(NO)
        key = self.panel.getch()


def main(stdscr):
    # Hide cursor
    curses.curs_set(0)
    screen = Screen(stdscr)
    date_counter = DateCounter()
    date_counter.register(screen.date)
    current_date = DATE
    date_counter.register(screen.tax)
    date_counter.register(screen.user)
    date_counter.register(screen.user.bank)
    date_counter.register(screen.finance)
    date_counter.register(screen)
    while True:
        time.sleep(1)
        current_date = current_date + TIMEDELTA
        date_counter.notify(current_date)
        key = screen.panel.getch()
        if key in screen.options:
            if type(screen.options[key]) == list:
                method, *args = screen.options[key]
                method(args[0])
            else:
                screen.options[key]()
        elif key == KEY_ESC:
            curses.endwin()
            break


if __name__ == '__main__':
    curses.wrapper(main)