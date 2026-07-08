from solver.rules.base import *
from forms.abc import *
from core.classes import zero, one


pow_add = RewriteSet(( # TODO generalised version
    a1**a2 * a1**a3,
    a1 ** (a2+a3)
))
pow_sub = RewriteSet((
    a1**a2 / a1**a3,
    a1 ** (a2-a3)
))
prod_exp = RewriteSet(( # TODO generalised version
    a1**a3 * a2**a3,
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
neg_pow1 = RewriteRule(
    form=a1**a2,
    target=one / a1**-a2
)
neg_pow2 = RewriteRule(
    form=one / a1**a2,
    target=a1**-a2
)
zero_pow = RewriteRule(
    form=a1 ** zero,
    target=one
)
rules = RewriteGroup((
    pow_add, pow_sub, prod_exp, frac_exp, pow_exp, neg_pow1, neg_pow2, zero_pow
))


if __name__ == '__main__':
    from core.classes import *
    x = Var('x')
    expr = (x**2+3/x-8*x)**0
    print(expr)
    new = rules.rewrite(expr)
    for i in new:
        print(str(i))