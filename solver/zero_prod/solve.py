from core.classes import *


def solve(expr: CORE_EXPR, main_solve):
    if isinstance(expr, Prod):
        solns = []
        for factor in expr.factors:
            soln = main_solve(factor)
            solns.extend(soln)
        return solns
    if isinstance(expr, Frac):
        return main_solve(expr.numer)
    if isinstance(expr, Exp):
        if isinstance(expr.power, Num) and expr.power > 0:
            return main_solve(expr.base)
    return []