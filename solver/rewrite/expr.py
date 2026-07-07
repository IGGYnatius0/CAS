from itertools import chain, combinations

from core.classes import *
from solver.rules import RULES


def rewrite(expr):
    vars = expr.get_vars
    if not vars:
        return []
    if isinstance(expr, Sum):
        return rewrite_sum(expr)
    if isinstance(expr, Prod):
        return rewrite_prod(expr)
    if isinstance(expr, Frac):
        return rewrite_frac(expr)
    if isinstance(expr, Exp):
        return rewrite_exp(expr)
    return expr # Num


def route(expr):
    pass


# Copied from itertools docs :)
def powerset(iterable):
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def rewrite_sum(expr: Sum):
    termss = powerset(expr.terms)
    iter(termss) # skip the first entry which is empty
    new_expr = []
    for terms in termss:
        if len(terms) == 1:
            new_expr.append(RULES.rewrite(terms[0]))
        else:
            new_expr.append(RULES.rewrite(Sum(terms)))
    new_expr.extend([rewrite(term) for term in expr.terms])
    return new_expr[::-1]


def rewrite_prod(expr: Prod):
    factorss = powerset(expr.factors)
    iter(factorss) # skip the first entry which is empty
    new_expr = []
    for factors in factorss:
        if len(factors) == 1:
            new_expr.append(RULES.rewrite(factors[0]))
        else:
            new_expr.append(RULES.rewrite(Sum(factors)))
    new_expr.extend([rewrite(term) for term in expr.factors])
    return new_expr[::-1]


def rewrite_frac(expr: Frac):
    RULES.rewrite(expr)


def rewrite_exp(expr: Exp):
    RULES.rewrite(expr)


if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17 / x + 12 / (x ** 2)
    print(rewrite(expr))