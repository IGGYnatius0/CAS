from functools import cached_property

from .registry import EXPRS
from .base import CoreFuncBase


class Func(CoreFuncBase):

    @cached_property
    def get_vars(self):
        return set()

    @cached_property
    def isnum(self):
        return False

    def copy(self):
        return type(self)(*[arg.copy() for arg in self.args])

    def apply(self, func, args=(), to_iter=False):
        # TODO implement path for to_iter
        return type(self)(*[func(arg, *args) for arg in self.args])


class SingleArgInit:
    def __init__(self, arg):
        self.args = [arg]


class MultiArgInit:
    def __init__(self, *args):
        self.args = args


EXPRS.func = Func