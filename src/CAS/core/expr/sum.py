from functools import cached_property

from .registry import EXPRS
from .base import CoreSumBase
from .utils import *


class Sum(CoreSumBase):
    def __init__(self, terms, flatten=True):
        if flatten:
            self.terms = []
            for term in terms:
                if isinstance(term, EXPRS.sum):
                    self.terms.extend(term.terms)
                else:
                    self.terms.append(make_expr(term))
        else:
            self.terms = terms
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

    def apply(self, func, args=(), to_iter=False):
        sum = [func(term, *args) for term in self.terms]
        if to_iter:
            return sum
        return Sum(sum)


EXPRS.sum = Sum