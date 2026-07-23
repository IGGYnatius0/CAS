from core.classes import *
from forms.abc import *
from forms.matcher import match
from solver.polynomial.rules import rules


def is_poly_expr(expr):
    if len(expr.get_vars) != 1:
        return False
    # temp = defaultdict(int)
    if isinstance(expr, Sum):
        for term in expr.terms:
            if isinstance(term, Num):
                # temp[zero] = term
                continue
            result = match(A * x ** B, term)
            if not result:
                return False
    else:
        result = match(A * x ** B, expr)
        if not result:
            return False
    return True


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