from solver.rewrite.base import RewriteSet
from forms.abc import *
from core.num import *


pow_add = RewriteSet(
    a1**a2 * a1**a3,
    a1 ** (a2+a3)
)
pow_sub = RewriteSet(
    a1**a2 / a1**a3,
    a1 ** (a2-a3)
)
prod_exp = RewriteSet(
    a1**32 * a2**a3,
    (a1*a2) ** a3
)
frac_exp = RewriteSet(
    a1**a3 / a2**a3,
    (a1/a2) ** a3
)
pow_exp = RewriteSet(
    (a1**a2) ** a3,
    a1 ** (a2*a3)
)
neg_pow = RewriteSet(
    a1**a2,
    one / a1**-a2
)


if __name__ == '__main__':
    from core.core_classes import *
    x = Var('x')
    expr = (2*x**3-x)**2 * (2*x**3-x)**3
    print(expr)
    print(prod_exp.rewrite(expr, simplify=True))