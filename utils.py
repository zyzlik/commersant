# -*- encoding: utf8 -*-


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
