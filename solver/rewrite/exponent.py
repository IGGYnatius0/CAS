from solver.rewrite.base import RewriteRule
from forms.abc import *


prod_exp = RewriteRule(
    a1**a2 * a1**a3,
    [a1 ** (a2+a3)]
)
quot_exp = RewriteRule(
    a1**a2 / a1**a3,
    [a1 ** (a2-a3)]
)


if __name__ == '__main__':
    from core.core_classes import *
    x = Var('x')
    expr = (2*x**3-x)**2 * (2*x**3-x)**3
    print(expr)
    print(prod_exp.rewrite(expr, simplify=True))