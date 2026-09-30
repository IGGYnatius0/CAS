from itertools import product
from collections import Counter

from CAS.core import *
from CAS.forms import match
from CAS.forms.abc import A, B, x


__all__ = ['Polynomial', 'Poly', 'poly_div', 'get_rational_roots']


class Polynomial:
    def __init__(self, poly, var=None):
        if isinstance(poly, CoreExprBase):
            if Polynomial.is_poly_expr(poly):
                self.coeffs = poly_to_coeffs(poly)
                self.deg = len(self.coeffs) - 1
                if var is None:
                    self.var = list(poly.get_vars)[0]
                else:
                    self.var = var
            else:
                raise ValueError('Input must be polynomial or coefficient list')
        elif isinstance(poly, list):
            self.coeffs = [make_expr(i) for i in poly]
            self.deg = len(self.coeffs) - 1
            if var is None:
                self.var = Var('x') # Do not change!!
            else:
                self.var = var
        elif isinstance(poly, Polynomial):
            self.coeffs = poly.coeffs.copy()
            self.deg = poly.deg
            self.var = poly.var
        else:
            raise ValueError('Input must be polynomial or coefficient list')

    def to_expr(self):
        terms = []
        for power, coeff in zip(range(self.deg, -1, -1), self.coeffs):
            terms.append(coeff * self.var ** power)
        return simplify(Sum(terms))

    @staticmethod
    def is_poly_expr(expr):
        if len(expr.get_vars) != 1:
            return False
        if isinstance(expr, Sum):
            for term in expr.terms:
                if term.isnum:
                    continue
                result = match(A * x ** B, term)
                if not result:
                    return False
                b = result['consts'][B]
                if not (isinstance(b, Num) and b.value > 0):
                    return False

        else:
            result = match(A * x ** B, expr)
            if not result:
                return False
            b = result['consts'][B]
            if not (isinstance(b, Num) and b > 0):
                return False
        return True

Poly = Polynomial


def poly_to_coeffs(poly):
    temp = {}
    if isinstance(poly, Sum):
        for term in poly.terms:
            if term.isnum:
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
    coeffs = [zero] * (max(temp.keys()).value + 1)
    for i, coeff in temp.items():
        coeffs[i.value] = coeff
    return coeffs[::-1]


def poly_div(poly1, poly2):
    poly1 = Polynomial(poly1)
    poly2 = Polynomial(poly2)
    if poly1.var != poly2.var:
        raise ValueError()
    if poly1.deg < poly2.deg:
        return poly1
    q_coeffs = [zero] * (poly1.deg - poly2.deg + 1)
    for i in range(len(q_coeffs)):
        q_coeffs[i] = simplify(Frac(poly1.coeffs[i], poly2.coeffs[0]))
        for j in range(poly2.deg + 1):
            poly1.coeffs[j+i] -= poly2.coeffs[j] * q_coeffs[i]
    return simplify(Polynomial(q_coeffs).to_expr() + Frac(poly1.to_expr(), poly2.to_expr()))


def get_rational_roots(poly):
    # Preprocess coefficients, I might turn this into a separate function in future
    # TODO pre check if coefficients are rational
    coeffs = poly.coeffs.copy()
    denom = Counter()
    for coeff in coeffs:
        denom_ = Counter()
        d = decomp(coeff)
        for base, power in d.items():
            if power < 0:
                denom_.update({base: -power.value})
        denom |= denom_
    denom = {base: Num(power) for base, power, in denom.items()}
    # Results from decomp cannot be modified in place because they are cached and mutable
    first = decomp(+coeffs[0]).copy()
    last = decomp(+coeffs[-1]).copy()
    first.pop(neg_one, None)
    last.pop(neg_one, None)
    first.update(denom)
    last.update(denom)
    first = simplify_decomp(first)
    last = simplify_decomp(last)
    # Actual computation
    numer_temp = [range(n.value + 1) for n in last.values()]
    denom_temp = [range(n.value + 1) for n in first.values()]
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
            roots.append(simplify(Frac(numer_factor, denom_factor)))
    roots = list(dict.fromkeys(roots))
    roots.extend([simplify(-root) for root in roots])
    return roots


if __name__ == '__main__':
    y = Var('y')
    poly = Poly(-Frac(2,3)*y**2+y-Frac(4,5))
    r = get_rational_roots(poly)
    [print(i) for i in r]
    print(len(r))