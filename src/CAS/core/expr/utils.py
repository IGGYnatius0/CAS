from collections import Counter
from decimal import Decimal

from .registry import EXPRS
from .base import CoreExprBase


__all__ = ['decomp2prod', 'make_expr']


def simplify_decomp(decomp: Counter) -> Counter:
    new_decomp = Counter()
    for base, power in decomp.items():
        new_decomp[base] = _simplify_decomp_dispatcher(power)
    return new_decomp


def _simplify_decomp_dispatcher(expr):
    if isinstance(expr, EXPRS.sum):
        return _simplify_decomp_sum(expr)
    if isinstance(expr, EXPRS.prod):
        return _simplify_decomp_prod(expr)
    return expr


def _simplify_decomp_sum(expr):
    const = 0
    exprs = []
    for term in expr.terms:
        term = _simplify_decomp_dispatcher(term)
        if isinstance(term, EXPRS.num):
            const += term.value
        else:
            exprs.append(term)
    if len(exprs) == 0:
        return EXPRS.num(const)
    if const != 0:
        exprs.append(const)
    if len(exprs) == 1:
        return exprs[0]
    return EXPRS.sum(exprs)


def _simplify_decomp_prod(expr):
    const = 1
    exprs = []
    for factor in expr.factors:
        factor = _simplify_decomp_dispatcher(factor)
        if isinstance(factor, EXPRS.num):
            if factor.value == 0:
                return EXPRS.zero
            const *= factor.value
        else:
            exprs.append(factor)
    if len(exprs) == 0:
        return EXPRS.num(const)
    if const != 1:
        exprs.append(const)
    if len(exprs) == 1:
        return exprs[0]
    return EXPRS.prod(exprs)


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