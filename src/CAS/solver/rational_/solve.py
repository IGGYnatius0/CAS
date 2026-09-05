from CAS.core.expr import CoreBaseExpr
from CAS.rational import *


def solve(expr: CoreBaseExpr, main_solve):
    if not is_rational_expr(expr):
        return []
    expr = rational_flatten(expr)
    return main_solve(expr)