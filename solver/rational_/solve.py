from core.classes import CORE_EXPR
from rational import *


def solve(expr: CORE_EXPR, main_solve):
    if not is_rational_expr(expr):
        return []
    expr = flatten_expr(expr)
    return main_solve(expr)