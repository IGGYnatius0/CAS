from functools import cached_property

from .registry import EXPRS
from .base import CoreFuncBase
from .utils import *


class Func(CoreFuncBase):

    @cached_property
    def get_vars(self):
        return set()

    @cached_property
    def isnum(self):
        return False

    def copy(self):
        return type(self)(*[arg.copy() for arg in self.args])

    def apply(self, func, *args):
        return type(self)(*[func(arg, *args) for arg in self.args])


class SingleArgInit:
    def __init__(self, arg):
        self.args = [arg]


class MultiArgInit:
    def __init__(self, *args):
        self.args = args


EXPRS.func = Func