# -*- encoding: utf8 -*-

from abc import ABCMeta, abstractmethod


class Observable(metaclass=ABCMeta):

    def __init__(self):
        self.observers = []

    def register(self, o):
        self.observers.append(o)

    def notify(self, msg):
        for o in self.observers:
            o.update(msg)


class Observer(metaclass=ABCMeta):

    @abstractmethod
    def update(self, msg):
        pass
