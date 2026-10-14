from decimal import Decimal
from functools import singledispatch

from .registry import FORMS
from .base import FormExprBase
from CAS.core import *


__all__ = ['make_form']


def make_formnum(num):
    if isinstance(num, Num):
        return FORMS.num(num.value)
    if not hasattr(num, 'as_integer_ratio'):
        raise ValueError(f"Input of type '{type(num)}' cannot be converted to FormNum")
    ratio = Decimal(str(num)).as_integer_ratio()
    if ratio[1] == 1:
        return FORMS.num(int(num))
    return FORMS.frac(*ratio)


def make_form(expr):
    try:
        return make_formnum(expr)
    except ValueError:
        if isinstance(expr, FormExprBase):
            return expr
        raise TypeError("Input expression must inherit from FormExprBase")