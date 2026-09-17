from functools import singledispatch, lru_cache
from collections import Counter

from CAS.core.expr import *
from CAS.polynomial import Poly


# TODO denom != 0
# TODO partial fractions?

__all__ = ['is_rational_expr', 'rational_flatten']


@lru_cache
@singledispatch
def is_rational_expr(expr: CoreExprBase) -> bool:
    return True

@is_rational_expr.register(Sum)
def _(expr) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for term in expr.terms:
        if not is_rational_expr(term):
            return False
    return True

@is_rational_expr.register(Prod)
def _(expr) -> bool:
    if Poly.is_poly_expr(expr):
        return True
    for factor in expr.factors:
        if not is_rational_expr(factor):
            return False
    return True

@is_rational_expr.register(Frac)
def _(expr) -> bool:
    if not is_rational_expr(expr.numer):
        return False
    if not is_rational_expr(expr.denom):
        return False
    return True

@is_rational_expr.register(Exp)
def _(expr) -> bool:
    if not isinstance(expr.power, Num):
        return False
    if not is_rational_expr(expr.base):
        return False
    return True



def rational_flatten(expr: CoreExprBase) -> CoreExprBase:
    denoms = True
    while denoms:
        denoms = get_denoms(expr)
        factors = decomp2prod(denoms).simplify()
        if isinstance(expr, Sum):
            expr = Sum([(term * factors).simplify() for term in expr.terms]).expand().simplify()
        else:
            expr = (expr * factors).expand().simplify()
    return expr



def get_denoms(expr: CoreExprBase) -> Counter:
    if isinstance(expr, Sum):
        denoms = Counter()
        for term in expr.terms:
            new_denoms = get_denoms(term)
            new_denoms = simplify_decomp(new_denoms)
            for base, power in new_denoms.items():
                new_denoms[base] = power.value
            denoms |= new_denoms
        return denoms
    if isinstance(expr, (Prod, Frac, Exp)):
        return -expr.decomp()
    return Counter()


if __name__ == '__main__':
    x = Var('x')
    expr = ((1+x)/(2+x)+3*x) / ((2+x)/(3+x)+4*x) + 5*x
    expr = expr.simplify()
    print(expr)
    print(rational_flatten(expr))
