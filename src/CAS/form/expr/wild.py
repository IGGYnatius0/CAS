from functools import cached_property

from .registry import FORMS
from .base import FormWildBase

from CAS.core import CoreExprBase
from CAS.exceptions import BadMethodError


class FormWild(FormWildBase):
    def __init__(self, sym, whitelist=(), blacklist=(), types=(CoreExprBase,)):
        self.sym = sym
        self.whitelist = tuple(whitelist)
        self.blacklist = tuple(blacklist)
        self.types = tuple(types)

    def match(self, expr, var_map):
        if self in var_map:
            if var_map[self] == expr:
                return FORMS.SingleConstraint(self, expr, var_map)
            return False
        if expr not in self.whitelist and self.whitelist:
            return False
        if expr in self.blacklist:
            return False
        if not isinstance(expr, self.types):
            return False
        var_map[self] = expr
        return FORMS.SingleConstraint(self, expr, var_map)

    @cached_property
    def isnum(self):
        return False

    @cached_property
    def isconst(self):
        return False

    @cached_property
    def get_consts(self):
        return set()

    @cached_property
    def get_vars(self):
        return {self}

    def apply(self, func, args=(), to_iter=False):
        raise BadMethodError("Cannot use .apply method on FormWild")

    def group_consts(self):
        return self

    def substitute_consts(self, const_map):
        return self


FORMS.wild = FormWild