from core.classes import *
from solver.zero_prod import solve as zero_solve
from solver.polynomial_ import solve as poly_solve
from solver.rational_ import solve as rational_solve


solvers = (
    zero_solve,
    poly_solve,
    rational_solve,
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
    expr = (x+3)/(x+1)-(x+1)/(x+3)-16/(x**2+4*x+3)
    print(solve(expr))