from CAS.core import *
from CAS.algebraic import *
from CAS.rational import rational_flatten


__all__ = ['solve']


def solve(expr: CoreExprBase, main_solve): # TODO back substitute to check correct or not
    expr = flatten_pows(expr)
    if not is_algebraic_expr(expr):
        return []
    bases, var_map = get_bases(expr)
    bases[-1] = rational_flatten(bases[-1])
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