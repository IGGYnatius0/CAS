from collections import Counter
from decimal import Decimal

from .registry import EXPRS


__all__ = ['decomp2prod', 'is_ext_num', 'clean_num']


def decomp2prod(decomp: Counter) -> EXPRS.prod:
    return EXPRS.prod([EXPRS.exp(base, power) for base, power in decomp.items()])


def is_ext_num(expr):
    return isinstance(expr, (int, float, Decimal))


def clean_num(num: int | float | Decimal):
    if isinstance(num, int):
        return EXPRS.num(num)
    ratio = num.as_integer_ratio()
    if ratio[1] == 1:
        return EXPRS.num(int(num))
    return EXPRS.frac(*ratio)