from core.classes import *
from solver.zero_prod import solve as zero_solve
from solver.polynomial_ import solve as poly_solve
from solver.rational_ import solve as rational_solve
from solver.algebraic_ import solve as alg_solve


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
    expr = (x+1)**Frac(1, 3) + (x+2)**Frac(1,3) - (2*x+3)**Frac(1,3)
    print(solve(expr))