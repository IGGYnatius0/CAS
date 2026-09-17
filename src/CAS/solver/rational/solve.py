from CAS.core.expr import CoreExprBase
from CAS.rational import *


def solve(expr: CoreExprBase, main_solve):
    if not is_rational_expr(expr):
        return []
    expr = rational_flatten(expr)
    return main_solve(expr)