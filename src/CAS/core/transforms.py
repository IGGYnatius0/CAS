from functools import singledispatch
from itertools import product

from .expr import *


@singledispatch
def expand(expr):
    return expr


@expand.register(Sum)
def _(sum):
    return Sum([expand(term) for term in sum.terms])


@expand.register(Frac)
def _(frac):
    return Frac(expand(frac.numer), expand(frac.denom))


@expand.register(Exp)
def _(exp):
    return Exp(expand(exp.base), expand(exp.power))


@expand.register(Prod)
def _(prod):
    to_expand = []
    for factor in prod.factors:
        factor = factor.expand()
        if isinstance(factor, Sum):
            to_expand.append(factor.terms)
        else:
            to_expand.append([factor])
    return Sum([Prod(term) for term in product(*to_expand)])