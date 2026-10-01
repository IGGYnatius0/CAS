from collections import defaultdict
from functools import cached_property

from .registry import EXPRS
from .base import CoreSumBase
from .utils import *


class Sum(CoreSumBase):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if isinstance(term, EXPRS.sum):
                self.terms.extend(term.terms)
            else:
                self.terms.append(make_expr(term))
        if not self.terms:
            self.terms = [EXPRS.zero]

    def substitute_vars(self, var_map):
        return Sum([term.substitute_vars(var_map) for term in self.terms])

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])

    @cached_property
    def isnum(self):
        for term in self.terms:
            if not term.isnum:
                return False
        return True

    def eval_nums(self):
        super().eval_nums()
        return sum([term.eval_nums() for term in self.terms])

    def copy(self):
        return Sum([term.copy() for term in self.terms])

    def group_nums(self):
        terms = [term.group_nums() for term in self.terms]
        temp = Sum(terms)
        if temp.isnum:
            return temp
        nums = []
        for i, term in reversed(list(enumerate(terms))):
            if term.isnum:
                nums.append(terms.pop(i))
        sum_ = Sum(terms)
        if len(nums) == 1:
            sum_.terms.append(nums[0])
        elif len(nums) > 1:
            sum_.terms.append(Sum(nums))
        return sum_


EXPRS.sum = Sum