from functools import cached_property

from .registry import FORMS
from .base import FormConstBase
from .utils import core2form
from CAS.intervals import REALS, from_str


class FormConst(FormConstBase):
    def __init__(self, sym, domain=REALS):
        self.sym = sym
        if isinstance(domain, str):
            self.domain = from_str(domain)
        else:
            self.domain = domain

    def match(self, expr, var_map):
        if not expr.isnum:
            return False
        if expr in self.domain:
            return FORMS.SingleConstraint(self, expr, var_map)
        return False

    @cached_property
    def isconst(self):
        return True

    @cached_property
    def get_consts(self):
        return {self}

    def substitute_consts(self, const_map):
        if self in const_map:
            return core2form(const_map[self])
        return self


FORMS.const = FormConst