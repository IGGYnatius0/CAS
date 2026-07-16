from itertools import product
from collections import Counter

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
    expanded = tuple(product(*to_expand))
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
    return [Prod(common.elements()) * Sum([Prod(elements(decomp)) for decomp in decomps])]


def elements(counter: Counter):
    output = []
    for item, count in counter.items():
        if int(count) == count: # Integer check
            output.extend([item.copy() for _ in range(int(count))])
        else:
            i, f = divmod(count, one)
            output.extend([item.copy() for _ in range(int(i))])
            output.append(Exp(item.copy(), f))
    return output


# TODO group, simplify


if __name__ == '__main__':
    x = Var('x')
    expr = x**2 + 2*x
    print(rewrite(expr)[0])