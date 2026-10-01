from collections import Counter
from decimal import Decimal

from .registry import EXPRS
from .base import CoreExprBase


__all__ = ['decomp2prod', 'make_expr']


def decomp2prod(decomp: Counter | dict):
    return EXPRS.prod([EXPRS.exp(base, power) for base, power in decomp.items()])


def make_num(num):
    if not hasattr(num, 'as_integer_ratio'):
        raise ValueError(f"Input of type '{type(num)}' cannot be converted to Num")
    ratio = Decimal(str(num)).as_integer_ratio()
    if ratio[1] == 1:
        return EXPRS.num(int(num))
    return EXPRS.frac(int(ratio[0]), int(ratio[1]))


def make_expr(expr):
    try:
        return make_num(expr)
    except ValueError:
        if isinstance(expr, CoreExprBase):
            return expr
        raise ValueError("Input expression must inherit from CoreExprBase")