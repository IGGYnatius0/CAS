from functools import cached_property

from .registry import FORMS
from .base import FormNumBase

from CAS.core import Num
from CAS.exceptions import BadMethodError


class FormNum(FormNumBase):
    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError("FormNum can only be initialized with int")
        self.value = value

    def match(self, expr, var_map):
        if isinstance(expr, Num) and expr.value == self.value:
            return FORMS.SingleConstraint(var_map=var_map)
        return False

    @cached_property
    def isnum(self):
        return True

    @cached_property
    def isconst(self):
        return True

    @cached_property
    def get_consts(self):
        return set()

    @cached_property
    def get_vars(self):
        return set()

    def apply(self, func, args, to_iter=False):
        raise BadMethodError("Cannot use .apply on FormNum")

    def group_consts(self):
        return self

    def substitute_consts(self, const_map):
        return self


FORMS.num = FormNum
FORMS.zero = FormNum(0)
FORMS.one = FormNum(1)
FORMS.neg_one = FormNum(-1)