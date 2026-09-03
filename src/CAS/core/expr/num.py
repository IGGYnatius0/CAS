from decimal import Decimal
from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseNum
from CAS.core.pfactor import pfactor


@EXPRS.register('num')
class Num(CoreBaseNum):
    def __init__(self, value, *args, **kwargs):
        Decimal.__init__(str(value), *args, **kwargs)

    def decomp(self):
        if int(self) == self:
            f = pfactor(self)
            return Counter({EXPRS['num'](base): EXPRS['num'](power) for base, power in f.items()})
        else:
            return EXPRS['frac'](*self.as_integer_ratio()).decomp()

    def expand(self):
        return self

    def factorize(self):
        return self

    def simplify(self):
        return self

    def substitute_vars(self, var_map):
        return self

    @cached_property
    def get_vars(self):
        return set()

    @cached_property
    def isnum(self):
        return True

    def copy(self):
        return self

    def eval_nums(self):
        return self

    def group_nums(self):
        return self

    @classmethod
    def is_num(cls, expr):
        return isinstance(expr, (int, float, Decimal, EXPRS['num']))

    def __repr__(self):
        return f"Num({str(self)})"

    def __hash__(self):
        return hash(('CoreNum', super().__hash__()))