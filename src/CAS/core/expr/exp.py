from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreExpBase
from .utils import *
from CAS.core.pfactor import pfactor


class Exp(CoreExpBase):
    def __init__(self, base, power):
        self.base = clean_num(base) if is_ext_num(base) else base
        self.power = clean_num(power) if is_ext_num(power) else power

    def decomp(self):
        if not self.power.isnum:
            return Counter({self: EXPRS.one})
        decomp = self.base.decomp()
        if isinstance(self.power, EXPRS.num):
            power = self.power.value
        else:
            power = self.power
        for expr in decomp:
            decomp[expr] *= power
        decomp = simplify_decomp(decomp)
        return decomp

    def expand(self):
        if isinstance(self.power, EXPRS.num) and int(
                self.power) == self.power and self.power > 0:
            return EXPRS.prod([self.base] * int(self.power)).expand()
        return self

    def factorize(self):
        return Exp(self.base.factorize(), self.power.factorize())

    @staticmethod
    def _pow_int_test(base: EXPRS.num, power: EXPRS.exp):
        f = pfactor(base.value)
        f_new = {}
        for p, n in f.items():
            if n % power.base.value != 0:
                return None
            f_new.update({p: n // power.base.value})
        result = 1
        for p, n in f_new.items():
            result *= p ** n
        return EXPRS.num(result)

    def simplify(self):
        """Simplifies the expression"""
        base = self.base.simplify()
        power = self.power.simplify()
        if isinstance(base, EXPRS.exp):
            power = (base.power * power).simplify()
            base = base.base
        if power == 1:
            return base
        if base == 1 or (power == 0 and base != 0):
            return EXPRS.one
        if base == 0 and power != 0:
            return EXPRS.zero
        if base == 0 and power == 0:
            return Exp(0, 0)
        if isinstance(base, EXPRS.num):
            if isinstance(power, EXPRS.num) and power > 0:
                # a^b where a and b are integers
                return EXPRS.num(base.value ** power.value)
            if isinstance(power, EXPRS.exp) and isinstance(power.base, EXPRS.num) and power.power == -1:
                # a^b where a is integer and b=1/int
                result = self._pow_int_test(base, power)
                if result:
                    return result
        return Exp(base, power)

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
        return Exp(self.base.copy(), self.power.copy())

    def eval_nums(self):
        return self.base.eval_nums() ** self.power.eval_nums()

    def group_nums(self):
        return Exp(self.base.group_nums(), self.power.group_nums())


EXPRS.exp = Exp