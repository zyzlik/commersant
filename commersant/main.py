# -*- encoding: utf8 -*-

import random
import time

from abc import ABCMeta, abstractmethod
from collections import OrderedDict

from constants import *
from menu import Menu, MultipleMenu
from observer import Observable, Observer
from utils import human_money, construct_date, validate_int, validate_month


YES = 1
NO = 0

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
            self.loan_rate = random.randint(*BANK_RATE_RANGE)
            self.deposit_rate = random.randint(*BANK_RATE_RANGE)

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

    def _count_max_width(self, product_dict):
        return max(len(i) for i in product_dict)

    def count_cars_width(self):
        return self._count_max_width(self.cars)

    def count_apts_width(self):
        return self._count_max_width(self.apartments)

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
            'car': '-',
            'oil': 0,
            'land': 0,
        }
        self.oil_benefit = {
            'bought': 0,
            'sold': 0,
            'benefit': 0
        }
        self.land_benefit = {
            'bought': 0,
            'sold': 0,
            'benefit': 0
        }
        self.marriage = False
        self.sick = False
        self.deposits = {construct_date(day=4): 10000}
        self.loans = {}
        self.bank = Bank()
        self.market = Market()
        self.date = None
        self.profit = 0
        self.birthday = construct_date(day=random.randrange(1,31), month=random.randrange(1,12), year=1990)

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
        if date.day == 1:
            self.profit = 0

    def get_payment(self, date):
        payment = self.deposits.pop(date)
        self.total_money += payment
        self.profit += payment

    def pay_loan(self, date):
        payment = self.loans.pop(date)
        self.total_money -= payment
        self.profit -= payment

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
            self.profit -= amount
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
            self.profit += amount
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

    def buy_car(self, car, price):
        if price < self.total_money:
            self.total_money -= price
            self.profit -= price
            self.property['car'] = car
            return True
        return False

    def buy_apartment(self, apt, price):
        if price < self.total_money:
            self.total_money -= price
            self.profit -= price
            self.property['apt'] = apt
            return True
        return False

    def buy_oil(self, amount, price):
        total_price = amount * price
        if total_price < self.total_money:
            self.total_money -= total_price
            self.profit -= total_price
            self.property['oil'] += amount
            self.oil_benefit['bought'] += amount
            self.oil_benefit['benefit'] -= total_price
            return True
        return False

    def buy_land(self, amount, price):
        total_price = amount * price
        if total_price < self.total_money:
            self.total_money -= total_price
            self.profit -= total_price
            self.property['land'] += amount
            self.land_benefit['bought'] += amount
            self.land_benefit['benefit'] -= total_price
            return True
        return False

    def sell_land(self, amount, price):
        total_money = amount * price
        self.total_money += total_money
        self.profit += total_money
        self.property['land'] -= amount
        self.land_benefit['sold'] += amount
        self.land_benefit['benefit'] += total_money

    def sell_oil(self, amount, price):
        total_money = amount * price
        self.total_money += total_money
        self.profit += total_money
        self.property['oil'] -= amount
        self.oil_benefit['sold'] += amount
        self.oil_benefit['benefit'] += total_money

    def sell_apt(self, price):
        if price:
            self.total_money += price
            self.profit += price
            self.property['apt'] = None

    def sell_car(self, price):
        if price:
            self.total_money += price
            self.profit += price
            self.property['car'] = None

    def is_enough_money(self, amount):
        if self.total_money > amount:
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
        self.panel.bkgd(' ', curses.color_pair(BLACK_WHITE))
        y = 0
        x = 2
        for key in self.options:
            s = '%s' % (key)
            self.panel.addstr(y, x, s, curses.color_pair(RED_WHITE))
            x += len(s)
            s = ':%s ' % (self.options[key])
            self.panel.addstr(y, x, s)
            x += len(s)


class TaxPanel(Panel, Observer):

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
        self.panel.bkgd(' ', curses.color_pair(BLACK_CYAN))
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


class FinancePanel(Panel, Observer):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(FinancePanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.house_rate = INITIAL_HOUSE_RATE
        self.land_rate = INITIAL_LAND_RATE

    def add_content(self):
        if not self.panel:
            self.create_panel()
        self.panel.clear()
        self.panel.bkgd(' ', curses.color_pair(BLACK_CYAN))
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        height, width = self.panel.getmaxyx()
        money_str = 'У вас на счету: %s %s' % (
            self.user.total_money, human_money(self.user.total_money))
        deposit_str = 'Вам должны: %s %s' % (
            sum(self.user.deposits.values()), human_money(sum(self.user.deposits.values())))
        loan_str = 'Вы должны: %s %s' % (
            sum(self.user.loans.values()), human_money(sum(self.user.loans.values())))
        month_income_str = 'Итого прибыль: %s %s' % (
            self.user.profit, human_money(self.user.profit))
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


class DatePanel(Panel, Observer):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(DatePanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.date = DATE

    def add_content(self):
        self.panel.clear()
        date_str = 'Сегодня: %s' % self.date.strftime('%d-%b-%Y')
        weekday_str = self.date.strftime('%A')
        self.panel.bkgd(' ', curses.color_pair(BLACK_CYAN))
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
        self.panel.bkgd(' ', curses.color_pair(WHITE_BLUE))
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
        if validate_int(amount):
            self.panel.addstr(8, 2, 'На какой срок (1-11 месяцев)? ')
            curses.echo()
            term = self.panel.getstr()
            if validate_int(term) and validate_month(term):
                self.user.new_deposit(int(amount), int(term))
        curses.noecho()

    def ask_for_loan(self):
        self.panel.addstr(7, 2, 'Какую сумму вы хотели бы взять? ')
        self.panel.refresh()
        curses.echo()
        amount = self.panel.getstr()
        if validate_int(amount):
            self.panel.addstr(8, 2, 'На какой срок (1-11 месяцев)? ')
            curses.echo()
            term = self.panel.getstr()
            if validate_int(term) and validate_month(term):
                self.user.new_loan(int(amount), int(term))
        curses.noecho()


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
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        self.panel.addstr(
            0, self.width // 2 - len(self.title) // 2, self.title, curses.color_pair(WHITE_BLUE)
        )
        self.panel.addstr(
            2, self.width // 2 - len(self.question) // 2, self.question, curses.color_pair(WHITE_BLUE)
        )


class MarketMenu(Menu):
    bg_color = curses.COLOR_BLUE
    fg_color = curses.COLOR_BLACK
    highlighted_bg_color = curses.COLOR_WHITE
    highlighted_fg_color = curses.COLOR_BLACK


class MarketAptMenu(MarketMenu):
    activate_btn = curses.KEY_RIGHT
    deactivate_btn = curses.KEY_LEFT


class MarketPanel(Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(MarketPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.title = ' Рынок '
        self.market = Market()
        self.car_pos = 1
        self.apt_pos = 0

    @staticmethod
    def _parse_item_string(s):
        name, price = s.split()
        return name, int(price)

    def purchase_response(self, response):
        title = "Продавец-консультант"
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.addstr("")
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        self.panel.addstr(
            0, self.width // 2 - len(title) // 2, title, curses.color_pair(WHITE_BLUE)
        )
        self.panel.addstr(
            self.height // 2 - 1, self.width // 2 - len(response) // 2, response, curses.color_pair(WHITE_BLUE)
        )

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        self.panel.addstr(
            0, self.width // 2 - len(self.title) // 2, self.title, curses.color_pair(WHITE_BLUE)
        )
        table_headers = ('А. Автомобили', 'D. Дома')
        self.panel.addstr(
            1, 2, table_headers[0], curses.color_pair(MAGENTA_BLUE)
        )
        self.panel.addstr(
            1, self.width - 10 - len(table_headers[1]), table_headers[1], curses.color_pair(MAGENTA_BLUE)
        )

        # Make strings for menu
        max_width = max(self.market.count_apts_width(), self.market.count_cars_width())
        cars_items = tuple('{car:<{max_width}}{price:>6}'.format(
            car=car,
            max_width=max_width,
            price = self.market.cars[car]['price']
        ) for car in self.market.cars)
        apts_items = tuple('{apt:<{max_width}}{price:>6}'.format(
            apt=apt,
            max_width=max_width,
            price=self.market.apartments[apt]['price']
        ) for apt in self.market.apartments)
        # Instantiate menus
        car_menu = MarketMenu(cars_items, self.panel, 3, 2)
        apt_menu = MarketAptMenu(apts_items, self.panel, 3, self.width // 2 + 4, active=False)
        menus = MultipleMenu((car_menu, apt_menu))
        # Get result
        res, menu = menus.start()
        if res == -1:
            return
        item, price = self._parse_item_string(menu.items[res])

        if item in self.market.cars:
            bought = self.user.buy_car(item, price)

        if item in self.market.apartments:
            bought = self.user.buy_apartment(item, price)

        if bought:
            self.purchase_response(' Поздравляем с покупкой! ')
        else:
            self.purchase_response(' Без денег не продаем! ')


class StockExchangePanel(Panel, Observer):
    oil_price = 0
    land_price = 0
    prices = [None] * 12
    open = True

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(StockExchangePanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.update_prices(DATE.month)

    def update_oil(self, increment=None):
        if increment is None:
            self.oil_price = random.randrange(*OIL_PRICE_RANGE)

    def update_land(self, increment=None):
        if increment is None:
            self.land_price = random.randrange(*LAND_PRICE_RANGE)

    def update_prices(self, month):
        self.update_oil()
        self.update_land()
        self.prices[month - 1] = (self.oil_price, self.land_price)

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        title = ' Биржа '
        self.panel.addstr(0, self.width // 2 - len(title) // 2, title, curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        for month, coord in enumerate(range(5, self.width - 5, (self.width - 5) // 12 )):
            self.panel.addstr(1, coord, str(month + 1), curses.color_pair(BLACK_BLUE))
            if self.prices[month] is not None:
                self.panel.addstr(2, coord, str(self.prices[month][1]), curses.color_pair(WHITE_BLUE))
                self.panel.addstr(3, coord, '{:>3}'.format(self.prices[month][0]), curses.color_pair(WHITE_BLUE))
        self.panel.addstr(4, 1, '_' * (self.width - 10), curses.color_pair(WHITE_BLUE))
        self.panel.addstr(
            5, 1, 'Z. Земля   -   {} за акр'.format(self.land_price), curses.color_pair(YELLOW_BLUE) | curses.A_BOLD
        )
        self.panel.addstr(
            6, 1, 'N. Нефть   -   {} за баррель'.format(self.oil_price), curses.color_pair(YELLOW_BLUE) | curses.A_BOLD
        )
        self.panel.addstr(
            8, 1, 'ESC - выход без покупки; Z, N - покупка', curses.color_pair(YELLOW_BLUE) | curses.A_BOLD
        )
        self.wait_for_key()

    def wait_for_key(self):
        key = self.panel.getch()
        if key == KEY_ESC:
            return
        elif key == KEY_Z:
            self.panel.addstr(9, 1, "Сколько акров: ", curses.color_pair(YELLOW_BLUE) | curses.A_BOLD)
            self.ask_for_land()
        elif key == KEY_N:
            self.panel.addstr(9, 1, "Сколько баррелей: ", curses.color_pair(YELLOW_BLUE) | curses.A_BOLD)
            self.ask_for_oil()
        else:
            self.wait_for_key()

    def not_enough_money(self):
        title = " Простите "
        message = "У вас нет столько денег"
        width = len(message) + 7
        height = 5
        win = self.panel.derwin(height, width, self.height // 2 - height // 2, self.width // 2 - width // 2)
        win.clear()
        win.box(curses.ACS_VLINE, curses.ACS_HLINE)
        win.addstr(0, width // 2 - len(title) // 2, title)
        win.addstr(2, width // 2 - len(message) // 2, message)
        win.keypad(1)
        key = win.getch()
        if key:
            return

    def ask_for_land(self):
        curses.echo()
        amount = self.panel.getstr()
        if validate_int(amount) and self.user.is_enough_money(int(amount) * self.land_price):
            self.user.buy_land(int(amount), self.land_price)
            curses.noecho()
        else:
            curses.noecho()
            self.not_enough_money()
            return

    def ask_for_oil(self):
        curses.echo()
        amount = self.panel.getstr()
        if validate_int(amount) and self.user.is_enough_money(int(amount) * self.oil_price):
            self.user.buy_oil(int(amount), self.oil_price)
            curses.noecho()
        else:
            curses.noecho()
            self.not_enough_money()
            return

    def update(self, date):
        if date.month == 1 and date.day == 1:
            self.prices.clear()
        if date.day == 1:
            self.update_prices(date.month)


class PropertyPanel(Panel):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(PropertyPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.market = kwargs.get('market')
        self.se = kwargs.get('stock_exchange')

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        title = ' Ваша собственность '
        col1_title = 'Наименование'
        col2_title = 'Цена'
        user_actions = 'ESC - выход без продажи; D, A, Z, N - продажа'
        apt_price = self.market.apartments.get(self.user.property['apt'], {}).get('price', 0)
        car_price = self.market.cars.get(self.user.property['car'], {}).get('price', 0)
        self.panel.addstr(0, self.width // 2 - len(title) // 2, title, curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(1, 5, col1_title, curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(1, self.width - len(col2_title) - 25, col2_title, curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(2, 1, "_" * (self.width - 25), curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(3, 1, 'D. ' + self.user.property['apt'], curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(3, self.width - len(col2_title) - 25, str(apt_price), curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(4, 1, 'A. Автомобиль ' + self.user.property['car'], curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(4, self.width - len(col2_title) - 25, str(car_price), curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(5, 1, 'Z. Земли ', curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(
            5, self.width - len(col2_title) - 25, str(self.user.property['land']), curses.color_pair(WHITE_BLUE) | curses.A_BOLD
        )
        self.panel.addstr(6, 1, 'N. Нефти', curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(
            6, self.width - len(col2_title) - 25, str(self.user.property['oil']), curses.color_pair(WHITE_BLUE) | curses.A_BOLD
        )
        self.panel.addstr(
            8, 1, user_actions, curses.color_pair(MAGENTA_BLUE)
        )
        self.wait_for_key()
        return

    def wait_for_key(self):
        key = self.panel.getch()
        if key == KEY_ESC:
            return
        elif key == KEY_Z:
            self.panel.addstr(9, 1, "Сколько акров: ", curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
            self.ask_for_land()
        elif key == KEY_N:
            self.panel.addstr(9, 1, "Сколько баррелей: ", curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
            self.ask_for_oil()
        elif key == KEY_D:
            self.user.sell_apt(self.market.apartments.get(self.user.property['apt'], {}).get('price', 0))
        elif key == KEY_A:
            self.user.sell_car(self.market.apartments.get(self.user.property['car'], {}).get('price', 0))

    def ask_for_land(self):
        curses.echo()
        amount = self.panel.getstr()
        if validate_int(amount) and self.user.property['land'] >= int(amount):
            self.user.sell_land(int(amount), self.se.land_price)
            curses.noecho()
        else:
            curses.noecho()
            self.not_enough('land')
            return

    def ask_for_oil(self):
        curses.echo()
        amount = self.panel.getstr()
        if validate_int(amount) and self.user.property['oil'] >= int(amount):
            self.user.sell_oil(int(amount), self.se.oil_price)
            curses.noecho()
        else:
            curses.noecho()
            self.not_enough('oil')
            return

    def not_enough(self, item):
        dct = {
            'oil': 'У вас нет столько нефти',
            'land': 'У вас нет столько земли'
        }
        title = " Простите "
        message = dct[item]
        width = len(message) + 7
        height = 5
        win = self.panel.derwin(height, width, self.height // 2 - height // 2, self.width // 2 - width // 2)
        win.clear()
        win.box(curses.ACS_VLINE, curses.ACS_HLINE)
        win.addstr(0, width // 2 - len(title) // 2, title)
        win.addstr(2, width // 2 - len(message) // 2, message)
        win.keypad(1)
        key = win.getch()
        if key:
            return


class SecretaryPanel(Panel, Observer):

    def __init__(self, parent, height, width, begin_y, begin_x, *args, **kwargs):
        super(SecretaryPanel, self).__init__(parent, height, width, begin_y, begin_x, *args, **kwargs)
        self.user = kwargs.get('user')
        self.heat = random.randrange(*HEAT_RANGE)

    def add_content(self):
        self.panel.clear()
        self.panel.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.panel.bkgd(' ', curses.color_pair(CYAN_BLUE))
        title = ' Секретарь '
        msg = 'На отопление дома и энергетическую установку в этом месяце'
        msg2 = 'понадобится %s баррл. нефти' % self.heat
        birthday_msg = 'Ваш день рождения %s-%s' % (self.user.birthday.day, self.user.birthday.month,)
        self.panel.addstr(0, self.width // 2 - len(title) // 2, title, curses.color_pair(WHITE_BLUE) | curses.A_BOLD)
        self.panel.addstr(1, 1, msg, curses.color_pair(CYAN_BLUE) | curses.A_BOLD)
        self.panel.addstr(2, 1, msg2, curses.color_pair(CYAN_BLUE) | curses.A_BOLD)
        self.panel.addstr(3, 1, birthday_msg, curses.color_pair(CYAN_BLUE) | curses.A_BOLD)
        self.panel.addstr(4, 1, '-' * (self.width - 20), curses.color_pair(CYAN_BLUE) | curses.A_BOLD)
        columns = ('', 'Куплено', 'Продано', 'Результат')
        oil_row = (
            'Нефти', self.user.oil_benefit['bought'], self.user.oil_benefit['sold'], self.user.oil_benefit['benefit']
        )
        land_row = (
            'Земли', self.user.land_benefit['bought'], self.user.land_benefit['sold'], self.user.land_benefit['benefit']
        )
        for i in range(len(columns)):
            self.panel.addstr(
                5, (self.width - 10) // 4 * (i + 1) - 8, columns[i], curses.color_pair(BLACK_BLUE)
            )
            self.panel.addstr(
                6, (self.width - 10) // 4 * (i + 1) - 8, str(oil_row[i]), curses.color_pair(BLACK_BLUE)
            )
            self.panel.addstr(
                7, (self.width - 10) // 4 * (i + 1) - 8, str(land_row[i]), curses.color_pair(BLACK_BLUE)
            )
        key = self.panel.getch()


    def update(self, msg):
        if msg.day == 1:
            self.heat = random.randrange(*HEAT_RANGE)


class Screen(Observer):

    def __init__(self, stdscr):
        self.panel = stdscr
        # Ожидание getch() не останавливает время
        self.panel.nodelay(YES)
        self.height, self.width = self.panel.getmaxyx()

        self.padding = 2
        self.side_panel_width = self.width // 2 - 2 * self.padding
        init_colors()

        self.panels = []

        self.panel.bkgd(curses.ACS_CKBOARD, curses.color_pair(BLACK_WHITE))
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
            self, 12, self.width - 30, self.height // 2 - 4, 15, user=self.user
        )
        self.stock_exchange = StockExchangePanel(
            self, 11, self.width - 12, self.height // 2 - 5, 6, user=self.user
        )
        self.property = PropertyPanel(
            self,
            self.height // 2,
            self.width - 16,
            self.height // 2 - 4, 8,
            user=self.user,
            market=self.market.market,
            stock_exchange=self.stock_exchange
        )
        self.secretary = SecretaryPanel(
            self,
            self.height // 2,
            self.width - 16,
            self.height // 2 - 4, 8,
            user=self.user
        )

        self.panels.append(self.menu)
        self.panels.append(self.date)
        self.panels.append(self.tax)
        self.panels.append(self.finance)

        self.update_panels()

        self.options = {
            curses.KEY_F1: self.show_bank,
            curses.KEY_F2: self.show_market,
            curses.KEY_F3: self.show_stock_exchange,
            curses.KEY_F4: self.show_property,
            curses.KEY_F9: self.show_secretary,
        }

    def update(self, msg):
        self.update_panels()

    def disable_panel(self, panel):
        if panel in self.panels:
            self.panels.remove(panel)
            panel.hide()
        self.update_panels()

    def enable_panel(self, panel):
        self.panels.append(panel)
        self.update_panels()

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
        curses.noecho()
        self.disable_panel(self.market)
        self.panel.nodelay(YES)

    def show_stock_exchange(self):
        self.enable_panel(self.stock_exchange)
        self.panel.nodelay(NO)
        curses.noecho()
        self.disable_panel(self.stock_exchange)
        self.panel.nodelay(YES)

    def show_property(self):
        self.enable_panel(self.property)
        self.panel.nodelay(NO)
        curses.noecho()
        self.disable_panel(self.property)
        self.panel.nodelay(YES)

    def show_secretary(self):
        self.enable_panel(self.secretary)
        self.panel.nodelay(NO)
        curses.noecho()
        self.disable_panel(self.secretary)
        self.panel.nodelay(YES)

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
    date_counter.register(screen.stock_exchange)
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
