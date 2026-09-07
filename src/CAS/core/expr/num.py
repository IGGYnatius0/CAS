from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseNum
from CAS.core.pfactor import pfactor


class Num(CoreBaseNum):
    def __init__(self, value):
        self.value = value

    def decomp(self):
        f = pfactor(self.value)
        return Counter({Num(base): Num(power) for base, power in f.items()})

    @cached_property
    def isnum(self):
        return True

    @staticmethod
    def is_num(x):
        return isinstance(x, (int, float))


EXPRS.num = Num

EXPRS.zero = Num(0)
EXPRS.one = Num(1)
EXPRS.neg_one = Num(-1)
EXPRS.inf = float('inf')
EXPRS.ninf = float('-inf')