from CAS.core import *
from CAS.polynomial import Poly
from .rules import rules
from .solvers import *
from CAS.solver.zero_prod import solve as zero_solve


def solve(expr: CoreExprBase, main_solve):
    expr = simplify(expand(expr))
    if not Poly.is_poly_expr(expr):
        return []
    expr = simplify(factorize(expr)) # Global factorize
    if not Poly.is_poly_expr(expr):
        return zero_solve(expr, main_solve)
    solns = rules.solve(Eqn(expr, zero))
    if solns:
        return solns
    solns = rational_root_solve(expr)
    if solns:
        return solns
    return []


if __name__ == '__main__':
    x = Var('x')
    print(solve((x+1)**3-3*x*(x+1)-(x+1), None))