from collections import Counter
from functools import cached_property
from itertools import product

from .registry import EXPRS
from .base import CoreProdBase
from .utils import *


class Prod(CoreProdBase):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if isinstance(factor, EXPRS.prod):
                self.factors.extend(factor.factors)
            else:
                self.factors.append(make_expr(factor))
        if not self.factors:
            self.factors = [EXPRS.one]

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    @cached_property
    def isnum(self):
        for factor in self.factors:
            if not factor.isnum:
                return False
        return True

    def copy(self):
        return Prod([factor.copy() for factor in self.factors])

    def apply(self, func, *args):
        return Prod([func(factor, *args) for factor in self.factors])


EXPRS.prod = Prod