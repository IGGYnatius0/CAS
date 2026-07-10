from itertools import chain, combinations
from core.classes import *


__all__ = ['rewrite']


def rewrite(eqn: Eqn):
    new_eqns = []
    new_eqns.extend(arrange_terms(eqn))
    new_eqns.extend(arrange_factors(eqn))
    return new_eqns


# Copied from itertools docs :D
def powerset(iterable):
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    return chain.from_iterable(combinations(iterable, r) for r in range(len(iterable) + 1))


def arrange_terms(eqn: Eqn):
    terms = []
    if isinstance(eqn.lhs, Sum):
        terms.extend(eqn.lhs.terms)
    elif eqn.lhs != zero:
        terms.append(eqn.lhs)
    if isinstance(eqn.rhs, Sum):
        terms.extend(eqn.rhs.terms)
    elif eqn.rhs != zero:
        terms.append(eqn.rhs)
    idxs = powerset(range(len(terms) - 1))
    next(idxs)
    new_eqns = []
    for idx in idxs:
        lhs, rhs = [], []
        for i, term in enumerate(terms):
            if i in idx:
                rhs.append((-term).simplify())
            else:
                lhs.append(term)
        if len(lhs) == 0:
            sum_lhs = zero
        elif len(lhs) == 1:
            sum_lhs = lhs[0]
        else:
            sum_lhs = Sum(lhs)
        if len(rhs) == 0:
            sum_rhs = zero
        elif len(rhs) == 1:
            sum_rhs = rhs[0]
        else:
            sum_rhs = Sum(rhs)
        new_eqns.append(Eqn(sum_lhs, sum_rhs))
    return new_eqns


def invert_factor(factor):
    if isinstance(factor, Frac):
        if factor.numer == one:
            return factor.denom
        return Frac(factor.denom, factor.numer)
    if isinstance(factor, Exp):
        return Exp(factor.base, (-factor.power).simplify())
    return one / factor


# TODO denom != 0
def arrange_factors(eqn: Eqn):
    factors = []
    if isinstance(eqn.lhs, Prod):
        factors.extend(eqn.lhs.factors)
    elif eqn.lhs != one:
        factors.append(eqn.lhs)
    if isinstance(eqn.rhs, Prod):
        factors.extend(eqn.rhs.factors)
    elif eqn.rhs != one:
        factors.append(eqn.rhs)
    idxs = powerset(range(len(factors) - 1))
    next(idxs)
    new_eqns = []
    for idx in idxs:
        lhs, rhs = [], []
        for i, factor in enumerate(factors):
            if i in idx:
                rhs.append(invert_factor(factor))
            else:
                lhs.append(factor)
        if len(lhs) == 0:
            prod_lhs = zero
        elif len(lhs) == 1:
            prod_lhs = lhs[0]
        else:
            prod_lhs = Prod(lhs)
        if len(rhs) == 0:
            prod_rhs = zero
        elif len(rhs) == 1:
            prod_rhs = rhs[0]
        else:
            prod_rhs = Prod(rhs)
        new_eqns.append(Eqn(prod_lhs, prod_rhs))
    return new_eqns


if __name__ == '__main__':
    x = Var('x')
    eqn = Eqn(x**2 - 3*x + 14, zero).simplify()
    print(eqn)
    new = arrange_terms(eqn)
    print(len(new))
    for i in new:
        print(i)