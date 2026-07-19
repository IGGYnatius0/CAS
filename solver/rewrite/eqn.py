from itertools import chain, combinations
from core.classes import *


def rewrite(eqn: Eqn):
    new_eqns = []
    new_eqns.extend(arrange_terms(eqn))
    new_eqns.extend(arrange_factors(eqn))
    return list(dict.fromkeys(new_eqns))


# Copied from itertools docs :D
def powerset(iterable):
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    return chain.from_iterable(combinations(iterable, r) for r in range(len(iterable) + 1))


def clean_terms(terms):
    if len(terms) == 0:
        return zero
    if len(terms) == 1:
        return terms[0]
    return Sum(terms)


def clean_factors(factors):
    if len(factors) == 0:
        return one
    if len(factors) == 1:
        return factors[0]
    return Prod(factors)


def arrange_terms(eqn: Eqn):
    terms = []
    if isinstance(eqn.lhs, Sum):
        terms.extend(eqn.lhs.terms)
    elif eqn.lhs != zero:
        terms.append(eqn.lhs)
    if isinstance(eqn.rhs, Sum):
        terms.extend([-term for term in eqn.rhs.terms])
    elif eqn.rhs != zero:
        terms.append(-eqn.rhs)
    idxs = powerset(range(len(terms) - 1))
    new_eqns = []
    for idx in idxs:
        lhs, rhs = [], []
        for i, term in enumerate(terms):
            if i in idx:
                rhs.append((-term).simplify())
            else:
                lhs.append(term)
        sum_lhs = clean_terms(lhs)
        sum_rhs = clean_terms(rhs)
        new_eqns.append(Eqn(sum_lhs, sum_rhs))
    return new_eqns


def invert_factor(factor):
    if isinstance(factor, Frac):
        if factor.numer == one:
            return factor.denom
        return Frac(factor.denom, factor.numer)
    if isinstance(factor, Exp):
        return Exp(factor.base, (-factor.power).simplify())
    return Exp(factor, neg_one)


def soft_decomp(expr):
    if isinstance(expr, Prod):
        return expr.factors
    if isinstance(expr, Frac):
        numer = soft_decomp(expr.numer)
        denom = [invert_factor(factor) for factor in soft_decomp(expr.denom)]
        return numer + denom
    return [expr]


# TODO denom != 0
def arrange_factors(eqn: Eqn):
    factors = []
    factors.extend(soft_decomp(eqn.lhs))
    factors.extend([invert_factor(factor) for factor in soft_decomp(eqn.rhs)])
    idxs = powerset(range(len(factors) - 1))
    new_eqns = []
    for idx in idxs:
        lhs, rhs = [], []
        for i, factor in enumerate(factors):
            if i in idx:
                rhs.append(invert_factor(factor))
            else:
                lhs.append(factor)
        prod_lhs = clean_factors(lhs)
        prod_rhs = clean_factors(rhs)
        new_eqns.append(Eqn(prod_lhs, prod_rhs))
    return new_eqns


if __name__ == '__main__':
    x = Var('x')
    eqn = Eqn(x*(x+1)/(x+2)*(x+3)**3, 1/(x+4)).simplify()
    print(eqn)
    new = arrange_factors(eqn)
    print(len(new))
    for i in new:
        print(i)