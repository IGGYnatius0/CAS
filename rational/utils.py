from functools import singledispatch, lru_cache
from collections import Counter

from core.classes import *
from polynomial import Poly


__all__ = ['is_rational_expr', 'flatten_expr']


@lru_cache
@singledispatch
def is_rational_expr(expr: CORE_EXPR) -> bool:
    return True


@lru_cache
@singledispatch
def is_flattened_expr(expr: CORE_EXPR) -> bool:
    return True


def flatten_expr(expr: CORE_EXPR) -> CORE_EXPR:
    while not Poly.is_poly_expr(expr):
        denoms = get_denoms(expr)
        factors = []
        for base, power in denoms.items():
            factors.append(Exp(base, power))
        factors = Prod(factors).simplify()
        if isinstance(expr, Sum):
            expr = Sum([(term * factors).simplify() for term in expr.terms]).expand().simplify()
        else:
            expr = (expr * factors).expand().simplify()
    return expr


@singledispatch
def get_denoms(expr: CORE_EXPR) -> Counter:
    return Counter()

####################
# is_rational_expr #
####################

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

#####################
# is_flattened_expr #
#####################

@is_flattened_expr.register(Sum)
def _(expr: Sum) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for term in expr.terms:
        if not is_flattened_expr(term):
            return False
    return True


@is_flattened_expr.register(Prod)
def _(expr: Prod) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for factor in expr.factors:
        if not is_flattened_expr(factor):
            return False
    return True


@ is_flattened_expr.register(Frac)
def _(expr: Frac) -> bool:
    return False


@is_flattened_expr.register(Exp)
def _(expr: Exp) -> bool:
    return expr.power > 0

##############
# get_denoms #
##############

@get_denoms.register(Sum)
def _(expr: Sum) -> Counter:
    denom = Counter()
    for term in expr.terms:
        denom |= get_denoms(term)
    return denom


@get_denoms.register(Prod)
@get_denoms.register(Frac)
@get_denoms.register(Exp)
def _(expr: Prod | Exp) -> Counter:
    return -expr.decomp()


if __name__ == '__main__':
    x = Var('x')
    expr = (
             ((2 * x ** 3 - 5 * x ** 2 + 3 * x - 1) / (x ** 2 + 2 * x + 1)) +
             ((x ** 4 - 3 * x ** 3 + 2 * x ** 2 - x + 4) / (2 * x ** 3 - x ** 2 + 3 * x - 2)) *
             ((3 * x ** 2 - 4 * x + 1) / (x ** 2 - x + 2))
     ) / (
             ((x ** 2 + 3 * x - 1) / (x - 2)) +
             ((2 * x ** 2 - x + 3) / (x ** 2 + 1))
     ) - (
             (x ** 3 - 2 * x ** 2 + 4 * x - 3) /
             ((x ** 2 + 1) * (x - 1) + 2 * x)
     )
    # expr = ((1+x)/(2+x)+3*x) / ((2+x)/(3+x)+4*x) + 5*x
    expr = expr.simplify()
    print(expr)
    print(flatten_expr(expr))
