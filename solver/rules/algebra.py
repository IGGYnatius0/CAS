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
    expanded = tuple(product(*to_expand))
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

    # Convert from Counter to list of Exp
    common_list = []
    for expr, power in common.items():
        common_list.append(Exp(expr, power))
    common_prod = Prod(common_list)

    terms_list = []
    for decomp in decomps:
        temp = []
        for expr, power in decomp.items():
            if power != zero:
                temp.append(Exp(expr, power))
        terms_list.append(Prod(temp))
    terms_sum = Sum(terms_list)

    return [common_prod * terms_sum]


# TODO group, simplify


if __name__ == '__main__':
    x = Var('x')
    expr = x**2 + 2*x
    print(rewrite(expr)[0])