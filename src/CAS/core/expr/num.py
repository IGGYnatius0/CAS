from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseNum
from CAS.core.pfactor import pfactor


@EXPRS.register('num')
class Num(CoreBaseNum):
    def decomp(self):
        return Counter({EXPRS['num'](base): EXPRS['num'](power) for base, power in pfactor(self).items()})

    @cached_property
    def isnum(self):
        return True