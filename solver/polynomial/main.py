from collections import defaultdict

from core.classes import *
from forms.matcher import match
from forms.abc import *


def is_poly_expr(expr):
    if len(expr.get_vars) != 1:
        return False
    # temp = defaultdict(int)
    if isinstance(expr, Sum):
        for term in expr.terms:
            if isinstance(term, Num):
                # temp[zero] = term
                continue
            result = match(A * x ** B, term)
            if not result:
                return False
            # temp[result['consts'][B]] = result['consts'][A]
    # coeffs = [zero] * int(max(temp.keys()) + 1)
    # for i, coeff in temp.items():
    #     coeffs[int(i)] = coeff
    # return coeffs[::-1]
    return True


if __name__ == '__main__':
    y = Var('x')
    print(is_poly_expr((Num(10)).simplify()))