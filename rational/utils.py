from functools import singledispatch
from collections import Counter

from core.classes import *
from polynomial import Poly


__all__ = ['is_rational_expr']


@singledispatch
def is_rational_expr(expr: CORE_EXPR) -> bool:
    return True


@singledispatch
def flatten_expr(expr: CORE_EXPR) -> CORE_EXPR:
    pass


@is_rational_expr.register(Sum)
def _(expr: Sum) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for term in expr.terms:
        if not is_rational_expr(term):
            return False
    return True


@is_rational_expr.register(Prod)
def _(expr: Prod) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for factor in expr.factors:
        if not is_rational_expr(factor):
            return False
    return True


@is_rational_expr.register(Frac)
def _(expr: Frac) -> bool:
    if not Poly.is_poly_expr(expr.numer):
        return False
    if not Poly.is_poly_expr(expr.denom):
        return False
    return True


@is_rational_expr.register(Exp)
def _(expr: Exp) -> bool:
    if not isinstance(expr.power, Num):
        return False
    if not (expr.power != 0 and expr.power == int(expr.power)):
        return False
    if not is_rational_expr(expr.base):
        return False
    return True


@flatten_expr.register(Sum)
def _(expr: Sum) -> Sum:
    decomps = [term.decomp() for term in expr.terms]
    mul = Counter()
    for decomp in decomps:
        mul |= -decomp
    mul


@flatten_expr.register(Prod)
def _(expr: Prod) -> Prod:
    pass


if __name__ == '__main__':
    flatten_
