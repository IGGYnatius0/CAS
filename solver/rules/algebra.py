from itertools import product

from core.classes import *


def rewrite(expr):
    return expand(expr) + factorise(expr)


def expand(expr):
    if not isinstance(expr, Prod):
        return []
    to_expand = []
    for factor in expr.factors:
        if isinstance(factor, Sum):
            to_expand.append(factor.terms)
        else:
            to_expand.append(factor)
    expanded = list(product(*to_expand))
    if len(expanded) == 1:
        return [expanded[0]]
    return [Sum(expanded)]


def factorise(expr):
    if not isinstance(expr, Sum):
        return []
    decomps = [term.decomp() for term in expr.terms]
    common = decomps[0].copy()
    for decomp in decomps[1:]:
        common &= decomp
    for i in range(len(decomps)):
        decomps[i].subtract(common)
    return [Prod(common.elements()) * Sum([Prod(decomp.elements()) for decomp in decomps])]


# TODO group, simplify


if __name__ == '__main__':
    x = Var('x')
    expr = x**2 + 2*x
    print(factorise(expr))