from itertools import product

from core.classes import *
from forms.matcher import match
from forms.abc import *


# Cubic, quartic, integer factoring

def extract_coeffs(poly):
    temp = {}
    if isinstance(poly, Sum):
        for term in poly.terms:
            if isinstance(term, Num):
                temp[zero] = term
                continue
            result = match(A * x ** B, term)
            if not result:
                return False
            temp[result['consts'][B]] = result['consts'][A]
    else:
        result = match(A * x ** B, poly)
        if not result:
            return False
        temp[result['consts'][B]] = result['consts'][A]
    coeffs = [zero] * int(max(temp.keys()) + 1)
    for i, coeff in temp.items():
        coeffs[int(i)] = coeff
    return coeffs[::-1]


def rational_root(coeffs):
    numer_temp = []
    denom_temp = []
    for n in coeffs[-1].decomp().values():
        numer_temp.append(range(int(n) + 1))
    for n in coeffs[0].decomp().values():
        denom_temp.append(range(int(n) + 1))
    numer_powers = product(*numer_temp)
    denom_powers = product(*denom_temp)
    numer_factors = []
    denom_factors = []
    for powers in numer_powers:
        factor = one
        for p, power in zip(coeffs[-1].decomp().keys(), powers):
            factor *= p ** power
        numer_factors.append(factor)
    for powers in denom_powers:
        factor = one
        for p, power in zip(coeffs[0].decomp().keys(), powers):
            factor *= p ** power
        denom_factors.append(factor)
    roots = []
    for numer_factor in numer_factors:
        for denom_factor in denom_factors:
            roots.append(Frac(numer_factor, denom_factor).simplify())
    roots = list(dict.fromkeys(roots))
    return roots


if __name__ == '__main__':
    y = Var('y')
    for root in rational_root([Num(54), 1, 1, Num(55)]):
        print(root)