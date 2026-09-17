from functools import singledispatch, lru_cache
from itertools import count

from CAS.core.expr import *
from CAS.core.utils import isrational
from CAS.rational import is_rational_expr


__all__ = ['flatten_pows', 'is_algebraic_expr', 'get_bases']


@singledispatch
def flatten_pows(expr: CoreExprBase) -> CoreExprBase:
    """Canonicalizes expressions to not have nested powers"""
    return expr

@flatten_pows.register(Sum)
def _(expr) -> Sum:
    return Sum([flatten_pows(term) for term in expr.terms])

@flatten_pows.register(Prod)
def _(expr) -> Prod:
    return Prod([flatten_pows(factor) for factor in expr.factors])

# Frac doesnt really matter because simplify will convert all Fracs to Exps
@flatten_pows.register(Frac)
def _(expr) -> Frac:
    return Frac(flatten_pows(expr.numer), flatten_pows(expr.denom))

# TODO have an option whether to apply the product rule
#  depending on whether to prioritise simpler expressions
#  or less variables in get_temp_vars
@flatten_pows.register(Exp)
def _(expr) -> Prod | Exp:
    # if isinstance(expr.base, Prod):
    #     return Prod([canonicalize(Exp(factor, expr.power)) for factor in expr.base.factors])
    if isinstance(expr.base, Exp):
        return Exp(expr.base.base, (expr.base.power * expr.power).simplify())
    return expr



@lru_cache
@singledispatch
def is_algebraic_expr(expr: CoreExprBase) -> bool:
    return True

@is_algebraic_expr.register(Sum)
def _(expr) -> bool:
    if is_rational_expr(expr):
        return True
    for term in expr.terms:
        if not is_algebraic_expr(term):
            return False
    return True

@is_algebraic_expr.register(Prod)
def _(expr) -> bool:
    if is_rational_expr(expr):
        return True
    for factor in expr.factors:
        if not is_algebraic_expr(factor):
            return False
    return True

@is_algebraic_expr.register(Frac)
def _(expr) -> bool:
    if not is_algebraic_expr(expr.numer):
        return False
    if not is_algebraic_expr(expr.denom):
        return False
    return True

@is_algebraic_expr.register(Exp)
def _(expr) -> bool:
    if not isrational(expr.power):
        return False
    if not is_algebraic_expr(expr.base):
        return False
    return True



def get_bases(expr: CoreExprBase):
    var_map = {}
    bases = []
    base = _get_bases(expr, var_map, bases, count())
    bases.append(base.simplify())
    return bases, var_map



@singledispatch
def _get_bases(expr: CoreExprBase, var_map: dict, bases: list, counter) -> None:
    return expr

@_get_bases.register(Sum)
def _(expr: Sum, var_map: dict, bases: list, counter) -> Sum:
    return Sum([_get_bases(term, var_map, bases, counter) for term in expr.terms])

@_get_bases.register(Prod)
def _(expr: Prod, var_map: dict, bases: list, counter) -> Prod:
    return Prod([_get_bases(factor, var_map, bases, counter) for factor in expr.factors])

@_get_bases.register(Frac)
def _(expr: Frac, var_map: dict, bases: list, counter) -> Frac:
    return Frac(_get_bases(expr.numer, var_map, bases, counter),
                _get_bases(expr.denom, var_map, bases, counter))

# TODO have an option to prioritise simpler expressions or less variables
#  Right now it is prioritising less variables
@_get_bases.register(Exp)
def _(expr: Exp, var_map: dict, bases: list, counter) -> Exp:
    base = expr.base.expand().simplify()
    power_numer = one
    power_denom = one
    for p, n in expr.power.decomp().items():
        if n > 0:
            power_numer *= p ** n
        elif n < 0:
            power_denom *= p ** -n
    power_numer = power_numer.simplify()
    power_denom = power_denom.simplify()
    base_with_pow = Exp(base, Exp(power_denom, neg_one))
    if base_with_pow in var_map:
        return Exp(var_map[base_with_pow], power_numer)
    # Create a new entry
    n = next(counter)
    new_var = Var(f'x{n}')
    var_map[base_with_pow] = new_var
    new_base = new_var ** power_denom + (-base).expand().simplify()
    bases.append(new_base)
    return Exp(var_map[base_with_pow], power_numer)


if __name__ == '__main__':
    x = Var('x')
    expr = 1/x**0.5 + 1/x**Frac(1,3) + x - 1
    bases, var_map = get_bases(expr)
    print(var_map)
    for base in bases:
        print(base)