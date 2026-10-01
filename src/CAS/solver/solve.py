from CAS.core import *
from .zero_prod import solve as zero_solve
from .polynomial import solve as poly_solve
from .rational import solve as rational_solve
from .algebraic import solve as alg_solve


solvers = (
    zero_solve,
    poly_solve,
    rational_solve,
    alg_solve,
)


def solve(expr): # TODO use SolveGroup?
    expr = simplify(expr)
    for solver in solvers:
        result = solver(expr, solve)
        if result:
            return [simplify(r) for r in result]
    return []


if __name__ == '__main__':
    x = Var('x')
    expr = (x+1)**Frac(1,3) + (x-1)**Frac(1,3) - x**Frac(1,3)
    print(solve(expr))