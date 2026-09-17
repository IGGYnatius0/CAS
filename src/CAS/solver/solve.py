from CAS.core.expr import *
from CAS.solver.zero_prod import solve as zero_solve
from CAS.solver.polynomial import solve as poly_solve
from CAS.solver.rational import solve as rational_solve
from CAS.solver.algebraic import solve as alg_solve


solvers = (
    zero_solve,
    poly_solve,
    rational_solve,
    alg_solve,
)


def solve(expr): # TODO use SolveGroup?
    expr = expr.simplify()
    for solver in solvers:
        result = solver(expr, solve)
        if result:
            return [r.simplify() for r in result]
    return []


if __name__ == '__main__':
    x = Var('x')
    expr = 1/x**0.5 - 1/x**Frac(1,3) + x - 1
    print(solve(expr))