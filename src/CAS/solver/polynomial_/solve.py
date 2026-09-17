from CAS.core.expr import *
from CAS.polynomial import Poly
from CAS.solver.polynomial_.rules import rules
from CAS.solver.polynomial_.solvers import *
from CAS.solver.zero_prod import solve as zero_solve


def solve(expr: CoreExprBase, main_solve):
    expr = expr.expand().simplify()
    expr = expr.factorize().simplify() # Global factorize
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