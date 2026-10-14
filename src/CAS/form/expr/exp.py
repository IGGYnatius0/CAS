from functools import cached_property

from .registry import FORMS
from .base import FormExpBase
from .utils import make_form
from CAS.core import zero, one, Exp


class FormExp(FormExpBase):
    def __init__(self, base, power):
        self.base = make_form(base)
        self.power = make_form(power)

    def match(self, expr, var_map):
        if expr.isnum:
            if expr == 0 or expr == 1:
                b1 = self.base.match(one, var_map.copy())
                if expr == 1 and b1:
                    return b1
                b0 = self.base.match(zero, var_map.copy())
                p0 = self.power.match(zero, var_map.copy())
                if expr == 0 and b0 and not p0:
                    return b0
            if self.isconst:
                return FORMS.SingleConstraint(self, expr, var_map.copy())
            return False
        if not isinstance(expr, Exp):
            return self.match(Exp(expr, one), var_map.copy())
        matches = FORMS.MultiConstraint(2)
        matches[0, 0] = self.base.match(expr.base, var_map.copy())
        matches[1, 1] = self.power.match(expr.power, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isnum(self):
        return self.base.isnum and self.power.isnum

    @cached_property
    def isconst(self):
        return self.base.isconst and self.power.isconst

    @cached_property
    def get_consts(self):
        return self.base.get_consts | self.power.get_consts

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    def apply(self, func, args=(), to_iter=False):
        exp = func(self.base, *args), func(self.power, *args)
        if to_iter:
            return exp
        return FormExp(*exp)


FORMS.exp = FormExp