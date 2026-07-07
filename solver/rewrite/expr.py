from itertools import chain, combinations
from copy import deepcopy

from core.classes import *
from core.num import *
from solver.rules import RULES


def rewrite(expr):
    vars = expr.get_vars
    if not vars:
        return []
    if isinstance(expr, Var):
        return RULES.rewrite(expr)
    if isinstance(expr, Sum):
        return rewrite_sum(expr)
    if isinstance(expr, Prod):
        return rewrite_prod(expr)
    if isinstance(expr, Frac):
        return rewrite_frac(expr)
    if isinstance(expr, Exp):
        return rewrite_exp(expr)
    return [expr] # Num


# Modified from itertools docs :)
def powerset(iterable):
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(iterable)
    # Skip first entry which is empty set
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


def rewrite_sum(expr: Sum):
    # Rewrites of subsets of expr.terms
    # FIXME only selected terms are getting rewritten, terms not in the power set are not included back into the sum
    subset_terms = powerset(expr.terms)
    new_expr = []
    for terms in subset_terms:
        if len(terms) == 1:
            new_expr.extend(RULES.rewrite(terms[0]))
        else:
            new_expr.extend(RULES.rewrite(Sum(terms)))
    # Rewrites of each expr.term, recursive
    for i, term in enumerate(expr.terms):
        for new_term in rewrite(term):
            copy_sum = expr.copy()
            copy_sum.terms[i] = new_term
            new_expr.append(copy_sum)
    return new_expr


def rewrite_prod(expr: Prod):
    # Rewrites of subsets of expr.factors
    subset_factors = powerset(expr.factors)
    new_expr = []
    for factors in subset_factors:
        if len(factors) == 1:
            new_expr.extend(RULES.rewrite(factors[0]))
        else:
            new_expr.extend(RULES.rewrite(Prod(factors)))
    # Rewrites of each expr.factor, recursive
    for i, factor in enumerate(expr.factors):
        for new_factor in rewrite(factor):
            copy_prod = expr.copy()
            copy_prod.factors[i] = new_factor
            new_expr.append(copy_prod)
    return new_expr


def rewrite_frac(expr: Frac):
    new_expr = []
    for numer in rewrite(expr.numer):
        new_expr.append(Frac(numer, expr.denom))
    for denom in rewrite(expr.denom):
        new_expr.append(Frac(expr.numer, denom))
    return new_expr


def rewrite_exp(expr: Exp):
    new_expr = []
    for base in rewrite(expr.base):
        new_expr.append(Exp(base, expr.power))
    for power in rewrite(expr.power):
        new_expr.append(Exp(expr.base, power))
    return new_expr


if __name__ == '__main__':
    x = Var('x')
    expr = x**2 + 1
    print(expr)
    new = rewrite(expr)
    for i in new:
        print(i)