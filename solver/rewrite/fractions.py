from solver.rewrite.base import *
from forms.abc import *
from core.num import *
from core.core_classes import Var

rules = RewriteGroup((
    RewriteRule(
        form=a1/a1,
        target=one
    ),
    RewriteSet((
        a1*(one/a2),
        a1/a2
    )),
    RewriteRule(
        a1*(a2/a3),
        (a1*a2)/a3
    ),
    RewriteSet((
        one/(a1/a2),
        a2/a1
    )),
    RewriteRule( # TODO generalised version
        form=(a1/a2)*(a3/a4),
        target=(a1*a3)/(a2*a4)
    ),
    RewriteRule( # TODO generalised version
        form=(a1/a2)+(a3/a4),
        target=(a1*a3+a2*a3)/(a2*a4)
    ),
    RewriteSet((
        (a1/a2)/a3,
        (a1/a2)*(one/a3)
    )),
    RewriteSet((
        a1/(a2/a3),
        a1*(a3/a2)
    )),
    RewriteSet((
        (a1/a2)/(a3/a4),
        (a1/a2)*(a4/a3)
    ))
))

if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17 / x + 12 / (x ** 2)
    print(expr)
    new = rules.rewrite(expr)
    for i in new:
        print(i)