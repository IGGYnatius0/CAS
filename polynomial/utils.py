from core.classes import *
from forms.matcher import match
from forms.abc import A, B, x


# TODO partial fractions?

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


if __name__ == '__main__':
    y = Var('y')
    numer = (y**3-2*y**2-4).simplify()
    denom = (y-3).simplify()
    print(poly_div(numer, denom))