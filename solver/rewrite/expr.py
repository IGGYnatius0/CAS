from itertools import chain, combinations

from core.classes import *
from solver.rules import RULES


__all__ = ['rewrite']


def rewrite(expr):
    return route_rewrite(expr) # TODO ordering eg whether to reverse or not


def route_rewrite(expr):
    vars = expr.get_vars
    if not vars:
        return []
    if isinstance(expr, Num):
        return []
    new_expr = RULES.rewrite(expr)
    if isinstance(expr, Sum):
        new_expr.extend(rewrite_sum(expr))
    elif isinstance(expr, Prod):
        new_expr.extend(rewrite_prod(expr))
    elif isinstance(expr, Frac):
        new_expr.extend(rewrite_frac(expr))
    elif isinstance(expr, Exp):
        new_expr.extend(rewrite_exp(expr))
    return list(dict.fromkeys(new_expr))


# Modified from itertools docs :)
def powerset(iterable):
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → (1,) (2,) (3,) (1,2) (1,3) (2,3)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))


def rewrite_sum(expr: Sum):
    # Rewrites of subsets of expr.terms
    subset_terms = tuple(powerset(expr.terms))
    zipped = zip(subset_terms, reversed(subset_terms))
    new_expr = []
    for terms, others in zipped:
        if len(terms) == 1:
            continue
        new_terms = RULES.rewrite(Sum(terms))
        new_expr.extend([Sum((new_term,) + others) for new_term in new_terms])
    # Rewrites of each expr.term, recursive
    for i, term in enumerate(expr.terms):
        for new_term in route_rewrite(term):
            copy_sum = expr.copy()
            copy_sum.terms[i] = new_term
            new_expr.append(copy_sum)
    return new_expr


def rewrite_prod(expr: Prod):
    # Rewrites of subsets of expr.factors
    subset_factors = tuple(powerset(expr.factors))
    zipped = zip(subset_factors, reversed(subset_factors))
    new_expr = []
    for factors, others in zipped:
        if len(factors) == 1:
            continue
        new_factors = RULES.rewrite(Prod(factors))
        new_expr.extend([Prod((new_factor,) + others) for new_factor in new_factors])
    # Rewrites of each expr.factor, recursive
    for i, factor in enumerate(expr.factors):
        for new_factor in route_rewrite(factor):
            copy_prod = expr.copy()
            copy_prod.factors[i] = new_factor
            new_expr.append(copy_prod)
    return new_expr


def rewrite_frac(expr: Frac):
    new_expr = []
    new_expr.extend([Frac(numer, expr.denom) for numer in route_rewrite(expr.numer)])
    new_expr.extend([Frac(expr.numer, denom) for denom in route_rewrite(expr.denom)])
    return new_expr


def rewrite_exp(expr: Exp):
    new_expr = []
    new_expr.extend([Exp(base, expr.power) for base in route_rewrite(expr.base)])
    new_expr.extend([Exp(expr.base, power) for power in route_rewrite(expr.power)])
    return new_expr


if __name__ == '__main__':
    x = Var('x')
    expr = x**2 + x
    print(expr)
    new = rewrite(expr)
    print(len(new))
    for i in new:
        print(i)