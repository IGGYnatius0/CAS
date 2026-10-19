from functools import cached_property

from .registry import EXPRS
from .base import CoreFuncBase
from .utils import make_expr


class Func(CoreFuncBase):
    @cached_property
    def get_vars(self):
        return set.union(*[arg.get_vars for arg in self.args])

    @cached_property
    def isnum(self):
        for arg in self.args:
            if not arg.isnum:
                return False
        return True

    def copy(self):
        return type(self)(*[arg.copy() for arg in self.args])

    def apply(self, func, args=(), to_iter=False):
        # TODO implement path for to_iter
        return type(self)(*[func(arg, *args) for arg in self.args])


class SingleArgInit:
    def __init__(self, arg):
        self.args = (make_expr(arg),)


class MultiArgInit:
    def __init__(self, *args):
        self.args = tuple(make_expr(arg) for arg in args)


EXPRS.func = Func