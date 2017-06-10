# -*- encoding: utf8 -*-

from datetime import date


def human_money(n):
    variants = {
        1: 'Гробль',
        2: 'Гробля',
        'rest': 'Гроблей'
    }
    if 10 < n < 15:
        return variants['rest']
    elif n % 10 == 1:
        return variants[1]
    elif 4 >= n % 10 >= 2:
        return variants[2]
    else:
        return variants['rest']


def construct_date(day=1, month=1, year=2017):
    try:
        return date(year, month, day)
    except ValueError:
        day -= 1
        return construct_date(day=day, month=month, year=year)


def validate_int(i):
    return i.isdigit()


def validate_month(month):
    return 12 >= int(month) > 0
