from functools import cached_property

from .registry import FORMS
from .base import FormConstBase
from CAS.core import Num
from CAS.interval import REALS, from_str


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
        return False

    @cached_property
    def get_consts(self):
        return set()

    @cached_property
    def get_vars(self):
        return set()

    def group_consts(self):
        return self

    def substitute_consts(self, const_map):
        if self in const_map:
            return Num(const_map[self].value)
        return self


FORMS.const = FormConst