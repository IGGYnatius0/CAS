from solver.rewrite.base import *
from forms.abc import *
from core.num import *


pow_add = RewriteSet((
    a1**a2 * a1**a3,
    a1 ** (a2+a3)
))
pow_sub = RewriteSet((
    a1**a2 / a1**a3,
    a1 ** (a2-a3)
))
prod_exp = RewriteSet((
    a1**32 * a2**a3,
    (a1*a2) ** a3
))
frac_exp = RewriteSet((
    a1**a3 / a2**a3,
    (a1/a2) ** a3
))
pow_exp = RewriteSet((
    (a1**a2) ** a3,
    a1 ** (a2*a3)
))
neg_pow = RewriteSet((
    a1**a2,
    one / a1**-a2
))
exp_rules = RewriteGroup((
    pow_add, pow_sub, prod_exp, frac_exp, pow_exp, neg_pow
))


if __name__ == '__main__':
    from core.core_classes import *
    x = Var('x')
    expr = x**-4
    print(expr)
    new = exp_rules.rewrite(expr, simplify=True)
    for i in new:
        print(str(i))