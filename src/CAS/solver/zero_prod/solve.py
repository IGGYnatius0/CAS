from CAS.core.expr import *


def solve(expr: CoreBaseExpr, main_solve):
    if isinstance(expr, Prod):
        solns = []
        for factor in expr.factors:
            if factor.isnum:
                continue
            soln = main_solve(factor)
            solns.extend(soln)
        return solns
    if isinstance(expr, Frac):
        return main_solve(expr.numer)
    if isinstance(expr, Exp):
        if expr.power.isnum and expr.power > 0: # FIXME
            return main_solve(expr.base)
    return []