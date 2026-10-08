from functools import cached_property

from .registry import EXPRS
from .base import CoreNumBase
from CAS.exceptions import BadMethodError


inf = float('inf')
ninf = float('-inf')

class Num(CoreNumBase):
    def __init__(self, value):
        if value not in (inf, ninf) and not isinstance(value, int):
            raise TypeError("Num can only be initialized with int")
        self.value = value

    @cached_property
    def get_vars(self):
        return set()

    @cached_property
    def isnum(self):
        return True

    def copy(self):
        return self # Can do this because ints are immutable

    def apply(self, func, args=(), to_iter=False):
        raise BadMethodError("Cannot use .apply method on Num")


EXPRS.num = Num

EXPRS.zero = Num(0)
EXPRS.one = Num(1)
EXPRS.neg_one = Num(-1)
EXPRS.inf = Num(inf)
EXPRS.ninf = Num(ninf)