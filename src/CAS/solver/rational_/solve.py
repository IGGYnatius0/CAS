from CAS.core.classes import CORE_EXPR
from CAS.rational import *


def solve(expr: CORE_EXPR, main_solve):
    if not is_rational_expr(expr):
        return []
    expr = rational_flatten(expr)
    return main_solve(expr)