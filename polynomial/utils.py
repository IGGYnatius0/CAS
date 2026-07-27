from itertools import product

from core.classes import *
from core.classes import CORE_EXPR
from forms.matcher import match
from forms.abc import A, B, x

# TODO add constraint that B must be integer
# TODO partial fractions?


__all__ = ['poly_to_coeffs', 'coeffs_to_poly', 'is_poly_expr', 'poly_div', 'get_rational_roots']


def _auto_coeffs(func):
    def wrapper(arg):
        if isinstance(arg, list):
            return func(arg)
        if isinstance(arg, CORE_EXPR):
            return func(poly_to_coeffs(arg))
        raise ValueError('Input must be polynomial or coefficient list')
    return wrapper


def _auto_poly(func):
    def wrapper(arg):
        if isinstance(arg, list):
            return func(coeffs_to_poly(arg))
        if isinstance(arg, CORE_EXPR):
            return func(arg)
        raise ValueError('Input must be polynomial or coefficient list')
    return wrapper


def is_poly_expr(expr):
    if len(expr.get_vars) != 1:
        return False
    if isinstance(expr, Sum):
        for term in expr.terms:
            if isinstance(term, Num):
                continue
            result = match(A * x ** B, term)
            if not result:
                return False
    else:
        result = match(A * x ** B, expr)
        if not result:
            return False
    return True


def poly_to_coeffs(poly):
    temp = {}
    if isinstance(poly, Sum):
        for term in poly.terms:
            if isinstance(term, Num):
                temp[zero] = term
                continue
            result = match(A * x ** B, term)
            if not result:
                raise ValueError('Input is not a polynomial')
            temp[result['consts'][B]] = result['consts'][A]
    else:
        result = match(A * x ** B, poly)
        if not result:
            raise ValueError('Input is not a polynomial')
        temp[result['consts'][B]] = result['consts'][A]
    coeffs = [zero] * int(max(temp.keys()) + 1)
    for i, coeff in temp.items():
        coeffs[int(i)] = coeff
    return coeffs[::-1]


def coeffs_to_poly(coeffs, var):
    deg = len(coeffs) - 1
    terms = []
    for power, coeff in zip(range(deg, -1, -1), coeffs):
        terms.append(coeff * var ** power)
    return Sum(terms).simplify()


@_auto_poly
def poly_div(poly1, poly2):
    coeffs1 = poly_to_coeffs(poly1)
    coeffs2 = poly_to_coeffs(poly2)
    deg1 = len(coeffs1) - 1
    deg2 = len(coeffs2) - 1
    if deg1 < deg2:
        return poly1
    q_coeffs = [zero] * (deg1 - deg2 + 1)
    for i in range(len(q_coeffs)):
        q_coeffs[i] = Frac(coeffs1[i], coeffs2[0]).simplify()
        for j in range(deg2 + 1):
            coeffs1[j+i] -= coeffs2[j] * q_coeffs[i]
    var = list(poly1.get_vars)[0]
    q_poly = coeffs_to_poly(q_coeffs, var)
    r_poly = coeffs_to_poly(coeffs1, var)
    return (q_poly + Frac(r_poly, poly2)).simplify()


@_auto_coeffs
def get_rational_roots(coeffs):
    first = abs(coeffs[0]).decomp()
    last = abs(coeffs[-1]).decomp()
    numer_temp = []
    denom_temp = []
    for n in last.values():
        numer_temp.append(range(int(n) + 1))
    for n in first.values():
        denom_temp.append(range(int(n) + 1))
    numer_powers = product(*numer_temp)
    denom_powers = product(*denom_temp)
    numer_factors = []
    denom_factors = []
    for powers in numer_powers:
        factor = one
        for p, power in zip(last.keys(), powers):
            factor *= p ** power
        numer_factors.append(factor)
    for powers in denom_powers:
        factor = one
        for p, power in zip(first.keys(), powers):
            factor *= p ** power
        denom_factors.append(factor)
    roots = []
    for numer_factor in numer_factors:
        for denom_factor in denom_factors:
            roots.append(Frac(numer_factor, denom_factor).simplify())
    roots = list(dict.fromkeys(roots))
    roots.extend([(-root).simplify() for root in roots])
    return roots


if __name__ == '__main__':
    y = Var('y')
    numer = (y**3-2*y**2-4).simplify()
    denom = (y-3).simplify()
    print(poly_div(numer, denom))