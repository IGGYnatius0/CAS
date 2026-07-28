from core.classes import *
from polynomial import Poly
from solver.polynomial.rules import rules
from solver.polynomial.solvers import *
from solver.zero_prod import solve as zero_solve


def get_terms(expr):
    if isinstance(expr, Sum):
        return expr.terms
    return [expr]


def solve(expr: CORE_EXPR, main_solve):
    expr = expr.expand().simplify()
    expr = expr.factorise().simplify() # Global factorise
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