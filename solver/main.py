from core.classes import *
from core.num import *
from forms.form_classes import *
from forms.forms import FORMS
from forms.formulas import FORMULAS


def match_form(expr):
    for i, form in enumerate(FORMS):
        result = match(form, expr)
        if result:
            return i, result
    return None


def replace_denoms(expr):
    """Returns a new expr with denominators removed, also returns the removed denominators"""
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


# def solve(expr):
#     # TODO add FORMULAS to known_forms and starting on rewrite logic
#     """Solver tries to solve by rewriting, but checking for form matches at every step"""
#     expr = expr.simplify()
#     expr, muls = replace_denoms(expr)
#     print(muls)
#     if muls:
#         muls = Prod(muls).simplify()
#         neq = solve(muls)
#     else:
#         neq = []
#     result = match_form(expr)
#     if result is not None:
#         form_id = result[0]
#         formulas = FORMULAS[form_id]
#         eq = []
#         for formula in formulas:
#             # Convert const_map from FormConst to Var
#             const_map = result[1]['consts']
#             var_map = {}
#             for key, value in const_map.items():
#                 var_map[Var(key.sym)] = value
#             ans = formula.substitute(var_map)
#             ans = ans.simplify()
#             eq.append(ans)
#         eq = list(set(eq))
#         if isinstance(neq, dict):
#             eq += neq['neq']
#             neq = neq['eq']
#         return {'eq': eq, 'neq': neq}
#     return None


def solve(expr):
    pass


if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17/x + 12/(x**2)
    print(solve(expr))