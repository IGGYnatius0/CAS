from functools import cached_property


from .registry import FORMS
from .base import FormVarBase
from CAS.core.expr import *


class FormVar(FormVarBase):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map):
        if not isinstance(expr, Var):
            return False
        if self in var_map:
            if var_map[self] == expr:
                return FORMS.SingleConstraint(self, expr, var_map)
            return False
        if expr in var_map.values():
            return False
        var_map[self] = expr
        return FORMS.SingleConstraint(self, expr, var_map)

    @cached_property
    def get_vars(self):
        return {self}


FORMS.var = FormVar