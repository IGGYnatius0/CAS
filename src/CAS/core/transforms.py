from functools import singledispatch
from itertools import product

from .expr import *
from .simplify import decomp, simplify_decomp


__all__ = ['expand', 'factorize']


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
    if isinstance(exp.power, Num) and exp.power > 0:
        return expand(Prod([exp.base] * exp.power.value))
    return exp


@expand.register(Eqn)
def _(eqn):
    return Eqn(expand(eqn.lhs), expand(eqn.rhs))


@expand.register(Prod)
def _(prod):
    to_expand = []
    for factor in prod.factors:
        factor = expand(factor)
        if isinstance(factor, Sum):
            to_expand.append(factor.terms)
        else:
            to_expand.append([factor])
    return Sum([Prod(term) for term in product(*to_expand)])


@singledispatch
def factorize(expr):
    return expr


@factorize.register(Prod)
def _(prod):
    return Prod([factorize(factor) for factor in prod.factors])


@factorize.register(Frac)
def _(frac):
    return Frac(factorize(frac.numer), factorize(frac.denom))


@factorize.register(Exp)
def _(exp):
    return Exp(factorize(exp.base), factorize(exp.power))


@factorize.register(Eqn)
def _(eqn):
    return Eqn(factorize(eqn.lhs), factorize(eqn.rhs))


@factorize.register(Sum)
def _(sum):
    decomps = [decomp(term).copy() for term in sum.terms]
    common = decomps[0].copy()
    for d in decomps[1:]:
        common &= d
    common = simplify_decomp(common)
    for i in range(len(decomps)):
        decomps[i].subtract(common)

    common_prod = decomp2prod(common)

    terms_list = []
    for d in decomps:
        temp = []
        for expr, power in d.items():
            if power != 0:
                temp.append(Exp(expr, power))
        terms_list.append(Prod(temp))
    terms_sum = Sum(terms_list)

    return Prod([common_prod, terms_sum])