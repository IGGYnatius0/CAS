from core.classes import *
from solver.zero_prod import solve as zero_solve
from solver.polynomial_ import solve as poly_solve


solvers = (
    zero_solve,
    poly_solve,
)


def solve(expr): # TODO use SolveGroup?
    expr = expr.simplify()
    for solver in solvers:
        result = solver(expr, solve)
        if result:
            return result
    return []


if __name__ == '__main__':
    x = Var('x')
    expr = (x+1)**3-3*x*(x+1)-(x+1)
    print(solve(expr))