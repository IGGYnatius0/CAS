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

    def substitute_vars(self, var_map):
        return Prod([term.substitute_vars(var_map) for term in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    @cached_property
    def isnum(self):
        for factor in self.factors:
            if not factor.isnum:
                return False
        return True

    def eval_nums(self):
        super().eval_nums()
        num = 1
        for factor in self.factors:
            num *= factor.eval_nums()
        return num

    def copy(self):
        return Prod([factor.copy() for factor in self.factors])

    def group_nums(self):
        factors = [factor.group_nums() for factor in self.factors]
        temp = Prod(factors)
        if temp.isnum:
            return temp
        nums = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isnum:
                nums.append(factors.pop(i))
        prod = Prod(factors)
        if len(nums) == 1:
            prod.factors.append(nums[0])
        elif len(nums) > 1:
            prod.factors.append(Prod(nums))
        return prod


EXPRS.prod = Prod