from functools import singledispatch, lru_cache
from collections import Counter

from core.classes import *
from forms.matcher import match
from forms.abc import A, B
from polynomial import Poly
from rational import *
from rational import rational_flatten as rational_flatten


__all__ = ['is_algebraic_expr', 'rational_flatten']


@lru_cache
@singledispatch
def is_algebraic_expr(expr: CORE_EXPR) -> bool:
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

#####################
# is_algebraic_expr #
#####################

@is_algebraic_expr.register(Sum)
def _(expr: Sum) -> bool:
    if is_rational_expr(expr):
        return True
    for term in expr.terms:
        if not is_algebraic_expr(term):
            return False
    return True


@is_algebraic_expr.register(Prod)
def _(expr: Prod) -> bool:
    if is_rational_expr(expr):
        return True
    for factor in expr.factors:
        if not is_algebraic_expr(factor):
            return False
    return True


@is_algebraic_expr.register(Frac)
def _(expr: Frac) -> bool:
    if not is_algebraic_expr(expr.numer):
        return False
    if not is_algebraic_expr(expr.denom):
        return False
    return True


@is_algebraic_expr.register(Exp)
def _(expr: Exp) -> bool:
    if not match(A/B, expr.power):
        return False
    if not is_algebraic_expr(expr.base):
        return False
    return True

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
    expr = expression = (
    (2*x**3 - 5*x**2 + 3*x - 1)**Frac(1, 2) +
    ((x**2 + 2*x + 1) / (x**2 - x + 2))**Frac(2, 3) -
    (3*x - 1)**Frac(3, 2) * ((x**2 + 3*x - 1) / (x - 2))**Frac(1, 3)
) / (
    ((x**2 + 1) / (2*x - 3))**Frac(3, 4) +
    ((x**3 - 2*x**2 + 4*x - 3) / (x**2 + x + 1))**Frac(1, 4) *
    (x**2 - x + 1)**Frac(2, 5)
) + (
    ((x**4 - 3*x**3 + 2*x**2 - x + 4) / (x**3 + 2*x**2 - x + 3))**Frac(1, 2) *
    (2*x + 1)**Frac(1, 3) -
    ((x**2 + 3*x + 2) / (x**2 - 3*x + 2))**Frac(3, 5)
) / (
    (x**2 - 4)**Frac(2, 3) +
    ((x**3 + x**2 + x + 1) / (x**3 - x**2 + x - 1))**Frac(1, 2) /
    (x + 2)**Frac(1, 4)
)
    # expr = ((1+x)/(2+x)+3*x) / ((2+x)/(3+x)+4*x) + 5*x
    expr = expr.simplify()
    print(expr)
    print(is_algebraic_expr(expr))
