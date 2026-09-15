from functools import cached_property

from .registry import FORMS
from .base import FormProdBase
from .utils import make_form
from CAS.core.expr import *


class FormProd(FormProdBase):
    def __init__(self, factors):
        # TODO functionality for products/large number of factors
        self.factors = [make_form(factor) for factor in factors]
        if not self.factors:
            self.factors = [FORMS.one]

    def match(self, expr, var_map):
        if expr.isnum:
            if self.isconst:
                return FORMS.SingleConstraint(self, expr, var_map.copy())
            if expr == 0:
                # If expr is zero, still can be matched if any of the factors match with zero
                # since a zero in FormProd will make the whole thing zero
                consts = [f for f in self.factors if f.isconst]
                if not consts:
                    return False
                return FormProd(consts).match(zero, var_map.copy())
            return False
        if isinstance(expr, Prod) and len(self.factors) != len(expr.factors):
            if len(expr.factors) > len(self.factors):
                return False
            # Padding by *1
            ones = [one] * (len(self.factors) - len(expr.factors))
            factors = expr.factors + ones
            return self.match(Prod(factors), var_map.copy())
        if not isinstance(expr, Prod):
            # Padding by *1
            ones = [one] * (len(self.factors) - 1)
            return self.match(Prod([expr] + ones), var_map.copy())
        matches = FORMS.MultiConstraint(len(self.factors))
        for i, ff in enumerate(self.factors):
            for j, ef in enumerate(expr.factors):
                matches[i, j] = ff.match(ef, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        for factor in self.factors:
            if not factor.isconst:
                return False
        return True

    def group_consts(self):
        """Groups all constants in this FormProd into a single FormProd"""
        factors = [factor.group_consts() for factor in self.factors]
        temp = FormProd(factors)
        if temp.isconst:
            return temp
        consts = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isconst:
                consts.append(factors.pop(i))
        if len(consts) == 1:
            factors.append(consts[0])
        elif len(consts) > 1:
            factors.append(FormProd(consts))
        return FormProd(factors)

    @cached_property
    def get_consts(self):
        return set.union(*[factor.get_consts for factor in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    def substitute_consts(self, const_map):
        return FormProd([factor.substitute_consts(const_map) for factor in self.factors])


FORMS.prod = FormProd