from CAS.core.expr import *
from CAS.core.abc import x, t
from CAS.polynomial import *


__all__ = ['rational_root_solve']


# Cubic, quartic, rational root thing


def _poly_typecheck(func):
    def wrapper(poly):
        if not isinstance(poly, Polynomial):
            poly = Polynomial(poly)
        return func(poly)
    return wrapper


@_poly_typecheck
def rational_root_solve(poly):
    roots = []
    test_roots = get_rational_roots(poly)
    for root in test_roots:
        result = poly_div(poly, (poly.var - root).simplify())
        if result == one:
            roots.append(root)
            break
        if Poly.is_poly_expr(result):
            roots.append(root)
            poly = Polynomial(result)
    return roots


# TODO not working :(
# @_poly_typecheck
# def cardano_cubic(cubic):
#     var = x if cubic.var == t else t
#     sub = {cubic.var: var - cubic.coeffs[1]/(3*cubic.coeffs[0])}
#     depressed = cubic.to_expr().substitute_vars(sub)
#     depressed = depressed.expand().simplify()
#     print(depressed)
#     depressed = Polynomial(depressed)
#     for i in range(1, depressed.deg + 1):
#         depressed.coeffs[i] /= depressed.coeffs[0]
#     depressed.coeffs[0] = one
#     p, q = depressed.coeffs[2], depressed.coeffs[3]
#
#     sol = (Frac(-q, 2) + ((Exp(q, 2) / 4) + (Exp(p, 3) / 27)) ** 0.5) ** Frac(1, 3) + \
#           (Frac(-q, 2) - ((Exp(q, 2) / 4 )+ (Exp(p, 3) / 27)) ** 0.5) ** Frac(1, 3)
#     print(sol.eval_nums())


if __name__ == '__main__':
    cubic = ((x-1)*(x-2)*(x-3)).expand().simplify()
    # print(cardano_cubic(cubic))