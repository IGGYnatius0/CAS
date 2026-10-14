from functools import cached_property

from .registry import FORMS
from .base import FormConstBase

from CAS.interval import REALS, from_str
from CAS.exceptions import BadMethodError


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
    def isnum(self):
        return False

    @cached_property
    def isconst(self):
        return True

    @cached_property
    def get_consts(self):
        return {self}

    @cached_property
    def get_vars(self):
        return set()

    def apply(self, func, args=(), to_iter=False):
        raise BadMethodError("Cannot use .apply method on FormConst")


FORMS.const = FormConst