from functools import cached_property

from .registry import FORMS
from .base import FormNumBase
from CAS.core.expr import Num


class FormNum(FormNumBase):
    def __init__(self, value):
        self.value = value

    def match(self, expr, var_map):
        if isinstance(expr, Num) and expr.value == self.value:
            return FORMS.SingleConstraint(var_map=var_map)
        return False

    @cached_property
    def isconst(self):
        return True


FORMS.num = FormNum
FORMS.zero = FormNum(0)
FORMS.one = FormNum(1)
FORMS.neg_one = FormNum(-1)