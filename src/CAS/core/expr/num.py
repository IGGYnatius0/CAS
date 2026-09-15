from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreNumBase
from CAS.core.pfactor import pfactor


class Num(CoreNumBase):
    def __init__(self, value):
        self.value = value

    def decomp(self):
        f = pfactor(self.value)
        return Counter({Num(base): Num(power) for base, power in f.items()})

    @cached_property
    def isnum(self):
        return True

    def eval_nums(self):
        return self.value


EXPRS.num = Num

EXPRS.zero = Num(0)
EXPRS.one = Num(1)
EXPRS.neg_one = Num(-1)
EXPRS.inf = Num(float('inf'))
EXPRS.ninf = Num(float('-inf'))