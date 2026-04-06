from core.core_classes import *
from core.num import *
from forms.known_forms import forms


def match_form(expr):
    pass


def replace_denoms(expr):
    if isinstance(expr, Sum):
        muls = []
        while True:
            for term in expr.terms:
                new_term, mul = replace_denoms(term)
                if mul != []:
                    muls.extend(mul)
                    break
            else:
                break
            temp = Prod([expr, *mul]).expand().simplify()
            terms = []
            for term in temp.terms:
                terms.append(Prod(term.decomp()).simplify())
            expr = Sum(terms)
        return expr, muls

    if isinstance(expr, Prod):
        muls = []
        for factor in expr.factors:
            new_factor, mul = replace_denoms(factor)
            if mul != []:
                muls.extend(mul)
        return Prod([expr, *muls]).expand().simplify(), muls

    if isinstance(expr, Frac):
        return expr.numer, [expr.denom]

    if isinstance(expr, Exp):
        if isinstance(expr.power, Num) and expr.power < 0:
            return expr, [Exp(expr.base, -expr.power)]

    return expr, []


def solve(expr):
    # TODO add formulas to known_forms and starting on rewrite logic
    """Solver tries to solve by rewriting, but checking for form matches at every step"""
    expr = expr.simplify()
    expr, muls = replace_denoms(expr) # later, need to have a constraint that muls != 0
    muls = Prod(muls).simplify()
    print(expr, muls)


if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17/x + 12/(x**2)
    print(expr)
    print(solve(expr))