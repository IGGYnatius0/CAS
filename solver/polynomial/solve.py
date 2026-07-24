from core.classes import *
from solver.polynomial.rules import rules
from polynomial import is_poly_expr


def get_terms(expr):
    if isinstance(expr, Sum):
        return expr.terms
    return [expr]


def solve(eqn: Eqn):
    terms = get_terms(eqn.lhs)
    terms.extend([-term for term in get_terms(eqn.rhs)])
    expr = Eqn(Sum(terms), 0).simplify()
    if is_poly_expr(expr):
        return rules.solve(expr)
    return []


if __name__ == '__main__':
    y = Var('x')
    print(solve(Eqn(1/y, 0)))