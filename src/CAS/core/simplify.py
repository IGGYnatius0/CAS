from functools import singledispatch, lru_cache
from collections import Counter

from .expr import *
from .pfactor import pfactor


@singledispatch
def decomp(expr):
    return Counter({expr: Num(1)})


@decomp.register(Num)
def _(num):
    return pfactor(num)


@decomp.register(Exp)
