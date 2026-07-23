from core.classes import *
from solver.polynomial import solve as poly_solve


solvers = (
    poly_solve,
)


def solve(expr): # TODO use SolveGroup?
    if isinstance(expr, CORE_TYPES) and not isinstance(expr, Eqn):
        eqn = Eqn(expr, zero)
    else:
        eqn = expr
    eqn = eqn.simplify()
    for solver in solvers:
        result = solver(eqn)
        if result:
            return result
    return []


if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17*x + 12*(x**2)
    print(solve(expr))