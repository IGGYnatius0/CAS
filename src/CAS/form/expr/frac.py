from functools import cached_property

from .registry import FORMS
from .base import FormFracBase
from .utils import make_form
from CAS.core import *


class FormFrac(FormFracBase):
    def __init__(self, numer, denom):
        self.numer = make_form(numer)
        self.denom = make_form(denom)

    def match(self, expr, var_map):
        if expr.isnum:
            if expr == 0:
                return self.numer.match(zero, var_map.copy())
            if self.isconst:
                return self.match(Frac(expr, one), var_map.copy())
            return False
        if not isinstance(expr, Frac):
            return self.match(Frac(expr, one), var_map.copy())
        matches = FORMS.MultiConstraint(2)
        matches[0, 0] = self.numer.match(expr.numer, var_map.copy())
        matches[1, 1] = self.denom.match(expr.denom, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        if not self.numer.isconst:
            return False
        if not self.denom.isconst:
            return False
        return True

    def group_consts(self):
        return FormFrac(self.numer.group_consts(), self.denom.group_consts())

    @cached_property
    def get_consts(self):
        return self.numer.get_consts | self.denom.get_consts

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    def substitute_consts(self, const_map):
        return FormFrac(self.numer.substitute_consts(const_map),
                        self.denom.substitute_consts(const_map))


FORMS.frac = FormFrac