from itertools import product

from core.classes import *
from forms.matcher import match
from forms.abc import A, B, x


__all__ = ['Polynomial', 'Poly', 'poly_div', 'get_rational_roots']


class Polynomial:
    def __init__(self, poly, var=None):
        if isinstance(poly, CORE_EXPR):
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
            self.coeffs = [Num(i) if Num.is_num(i) else i for i in poly]
            self.deg = len(self.coeffs) - 1
            if var is None:
                self.var = Var('x')
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
        return Sum(terms).simplify()

    @staticmethod
    def is_poly_expr(expr):
        if len(expr.get_vars) != 1:
            return False
        if isinstance(expr, Sum):
            for term in expr.terms:
                if term.isnum:
                    continue
                result = match(A * x ** B, term) # TODO if A is 0.75 it will be simplified to 3 * 2^-2 which fails this
                if not result:
                    return False
                b = result['consts'][B]
                if not (b == int(b) and b > 0):
                    return False

        else:
            result = match(A * x ** B, expr)
            if not result:
                return False
            b = result['consts'][B]
            if not (b == int(b) and b > 0):
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
    coeffs = [zero] * int(max(temp.keys()) + 1)
    for i, coeff in temp.items():
        coeffs[int(i)] = coeff
    return coeffs[::-1]


def poly_div(poly1, poly2):
    poly1 = Polynomial(poly1)
    poly2 = Polynomial(poly2)
    if poly1.deg < poly2.deg:
        return poly1
    q_coeffs = [zero] * (poly1.deg - poly2.deg + 1)
    for i in range(len(q_coeffs)):
        q_coeffs[i] = Frac(poly1.coeffs[i], poly2.coeffs[0]).simplify()
        for j in range(poly2.deg + 1):
            poly1.coeffs[j+i] -= poly2.coeffs[j] * q_coeffs[i]
    return (Polynomial(q_coeffs).to_expr() + Frac(poly1.to_expr(), poly2.to_expr())).simplify()


def get_rational_roots(poly):
    first = abs(poly.coeffs[0]).decomp()
    last = abs(poly.coeffs[-1]).decomp()
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
    expr = (y + 1) ** Frac(1, 3) + (y + 2) ** Frac(1, 3) - (2 * y + 3) ** Frac(1, 3)
    print(Poly.is_poly_expr(expr))