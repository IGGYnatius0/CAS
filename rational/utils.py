from functools import singledispatch
from collections import Counter

from core.classes import *
from polynomial import Poly


__all__ = ['is_rational_expr', 'flatten_expr']


@singledispatch
def is_rational_expr(expr: CORE_EXPR) -> bool:
    return True


@singledispatch
def is_flattened_expr(expr: CORE_EXPR) -> bool:
    return True


def flatten_expr(expr: CORE_EXPR) -> CORE_EXPR:
    while not is_flattened_expr(expr):
        expr = flatten_expr_dispatcher(expr)
        print(expr)
    return expr


@singledispatch
def flatten_expr_dispatcher(expr: CORE_EXPR) -> CORE_EXPR:
    return expr

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

###########################
# flatten_expr_dispatcher #
###########################

@flatten_expr_dispatcher.register(Sum)
def _(expr: Sum) -> CORE_EXPR:
    decomps = [term.decomp() for term in expr.terms]
    mul = Counter()
    for decomp in decomps:
        mul |= -decomp
    factors = []
    # TODO make all instances of having to resconstruct a Prod from its decomp
    # and make it use the pattern shown here (ie appending into a factors list)
    # instead of doing expr *= base ** power
    for base, power in mul.items():
        factors.append(Exp(base, power))
    mul_prod = Prod(factors)
    # expand() is not used here to prevent unnecessary expanding of powers
    # only need to distribute mul_expr to terms
    return Sum([term * mul_prod for term in expr.terms]).simplify()


@flatten_expr_dispatcher.register(Prod)
@flatten_expr_dispatcher.register(Frac)
@flatten_expr_dispatcher.register(Exp)
def _(expr: Prod | Frac | Exp) -> CORE_EXPR:
    decomp = +expr.decomp()
    factors = []
    for base, power in decomp.items():
        factors.append(Exp(base, power))
    return Prod(factors).simplify()


if __name__ == '__main__':
    x = Var('x')
    expr = (
    ((3*x**5 - 2*x**4 + 7*x**3 - 9*x**2 + 4*x - 1) / (2*x**4 + 5*x**3 - 3*x**2 + x + 6)) +
    ((x**7 - 4*x**6 + 2*x**5 - 8*x**4 + 3*x**3 - 5*x**2 + 7*x - 2) / (x**5 - 3*x**4 + 6*x**3 - 2*x**2 + 5*x - 4)) *
    ((2*x**8 + 3*x**7 - 5*x**6 + 7*x**5 - 11*x**4 + 13*x**3 - 17*x**2 + 19*x - 23) /
     (x**6 + 4*x**5 - 3*x**4 + 2*x**3 - 7*x**2 + 5*x + 1)) -
    ((x**4 - 5*x**3 + 9*x**2 - 7*x + 2) / (3*x**3 - 2*x**2 + 4*x - 1)) /
    ((x**3 + 2*x**2 - 3*x + 1) / (x**2 - x + 1) + (x**2 + x + 1) / (x - 2))
) / (
    ((2*x**6 - 5*x**5 + 3*x**4 - 7*x**3 + 8*x**2 - 4*x + 1) / (x**4 - x**3 + 2*x**2 - 3*x + 5)) +
    ((x**3 + 4*x**2 - 2*x + 1) / (2*x**3 - 3*x**2 + x - 4)) *
    ((3*x**4 - 2*x**3 + 5*x**2 - 7*x + 11) / (x**2 + 3*x - 2)) -
    ((x**5 - 2*x**4 + 3*x**3 - 4*x**2 + 5*x - 6) / (x**3 + x**2 + x + 1))
) + (
    ((x**7 + 5*x**6 - 3*x**5 + 9*x**4 - 2*x**3 + 6*x**2 - 8*x + 4) /
     (x**6 - 2*x**5 + 3*x**4 - 5*x**3 + 7*x**2 - 11*x + 13)) /
    ((x**3 - 2*x**2 + 3*x - 1) / (x**2 + 2*x - 3) + (2*x**2 - 3*x + 4) / (x**2 - x + 2))
) - (
    ((2*x**4 + 3*x**3 - 4*x**2 + 5*x - 6) * (x**3 - 2*x**2 + 3*x - 4) +
     (3*x**5 - 2*x**4 + x**3 - 5*x**2 + 7*x - 1)) /
    ((x**2 + x + 1) * (2*x**2 - 3*x + 1) - (x**3 + 2*x**2 - x + 3))
)
    expr = expr.simplify()
    print(expr)
    print(flatten_expr(expr))
