from core.classes import *
from algebraic import *


__all__ = ['solve']


def solve(expr: CORE_EXPR, main_solve): # TODO FORGOT TO FLATTEN!!
    expr = canonicalize(expr)
    if not is_algebraic_expr(expr):
        return []
    bases, var_map = get_bases(expr)
    ordering = list(var_map.values())
    main_var = tuple(expr.get_vars)[0]
    ordering.append(main_var)
    ordering = tuple(ordering)
    gb = groebner_basis(bases, ordering)
    for basis in gb:
        vars_ = tuple(basis.get_vars)
        if vars_ == (main_var,):
            return main_solve(basis)
    return []

if __name__ == "__main__":
    x = Var('x')
    expr = (x+1)**Frac(1, 3) + (x-1)**Frac(1,3) - x**Frac(1,3)
    solve(expr)