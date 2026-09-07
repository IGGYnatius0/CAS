from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseExp
from .utils import *


@EXPRS.register('exp')
class Exp(CoreBaseExp):
    def __init__(self, base, power):
        self.base = clean_num(base) if is_ext_num(base) else base
        self.power = clean_num(power) if is_ext_num(power) else power

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        if isinstance(self.power, EXPRS.num):
            return Counter({self.base: self.power})
        return Counter({self: 1})

    def expand(self):
        if isinstance(self.power, EXPRS.num) and int(
                self.power) == self.power and self.power > 0:
            return EXPRS.prod([self.base] * int(self.power)).expand()
        return self

    def factorize(self):
        return EXPRS.exp(self.base.factorize(), self.power.factorize())

    def simplify(self):
        """Simplifies the expression"""
        base = self.base.simplify()
        power = self.power.simplify()
        if power == 1:
            return base
        if base == 1 or (power == 0 and base != 0):
            return 1
        if base == 0 and power != 0:
            return 0
        if base == 0 and power == 0:
            return EXPRS.exp(0, 0)
        if isinstance(base, EXPRS.num) and isinstance(power, EXPRS.num):
            if base == int(base) and power == int(power) and power > 0:
                return base ** power
            result = base ** power
            if result == int(result):
                return result
        return EXPRS.exp(base, power)

    def substitute_vars(self, var_map):
        return self.base.substitute_vars(var_map) ** self.power.substitute_vars(
            var_map)

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    @cached_property
    def isnum(self):
        return self.base.isnum and self.power.isnum

    def copy(self):
        return EXPRS.exp(self.base.copy(), self.power.copy())

    def eval_nums(self):
        return self.base.eval_nums() ** self.power.eval_nums()

    def group_nums(self):
        return EXPRS.exp(self.base.group_nums(), self.power.group_nums())