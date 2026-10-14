from functools import cached_property

from .registry import FORMS
from .base import FormSumBase
from .utils import make_form
from CAS.core import zero, Sum


class FormSum(FormSumBase):
    def __init__(self, terms):
        # TODO functionality for summations/large number of terms
        self.terms = [make_form(term) for term in terms]
        if not self.terms:
            self.terms = [FORMS.zero]

    def match(self, expr, var_map):
        if expr.isnum:
            if self.isconst:
                return FORMS.SingleConstraint(self, expr, var_map.copy())
            if expr == 0:
                # FormSum can match zero if all terms can match zero
                zeros = [zero] * len(self.terms)
                return self.match(Sum(zeros), var_map.copy())
            return False
        if isinstance(expr, Sum) and len(self.terms) != len(expr.terms):
            if len(expr.terms) > len(self.terms):
                return False
            # Padding by +0
            zeros = [zero] * (len(self.terms) - len(expr.terms))
            terms = expr.terms + zeros
            return self.match(Sum(terms), var_map.copy())
        if not isinstance(expr, Sum):
            # Padding by +0
            zeros = [zero] * (len(self.terms) - 1)
            return self.match(Sum([expr] + zeros), var_map.copy())
        matches = FORMS.MultiConstraint(len(self.terms))
        for i, ft in enumerate(self.terms):
            for j, et in enumerate(expr.terms):
                match = ft.match(et, var_map.copy())
                if match:
                    matches[i, j] = match
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isnum(self):
        for term in self.terms:
            if not term.isnum:
                return False
        return True

    @cached_property
    def isconst(self):
        for term in self.terms:
            if not term.isconst:
                return False
        return True

    @cached_property
    def get_consts(self):
        return set.union(*[term.get_consts for term in self.terms])

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])

    def apply(self, func, args=(), to_iter=False):
        sum = [func(term, *args) for term in self.terms]
        if to_iter:
            return sum
        return FormSum(sum)


FORMS.sum = FormSum