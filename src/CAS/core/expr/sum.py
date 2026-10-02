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

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])

    @cached_property
    def isnum(self):
        for term in self.terms:
            if not term.isnum:
                return False
        return True

    def copy(self):
        return Sum([term.copy() for term in self.terms])

    def apply(self, func, *args, to_list=False):
        sum = Sum([func(term, *args) for term in self.terms])
        if to_list:
            return sum.terms
        return sum


EXPRS.sum = Sum