from functools import cached_property

from .registry import EXPRS
from .base import CoreExpBase
from .utils import make_expr


class Exp(CoreExpBase):
    def __init__(self, base, power):
        self.base = make_expr(base)
        self.power = make_expr(power)

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    @cached_property
    def isnum(self):
        return self.base.isnum and self.power.isnum

    def copy(self):
        return Exp(self.base.copy(), self.power.copy())

    def apply(self, func, *args, to_list=False):
        exp = Exp(func(self.base, *args), func(self.power, *args))
        if to_list:
            return exp.base, exp.power
        return exp


EXPRS.exp = Exp