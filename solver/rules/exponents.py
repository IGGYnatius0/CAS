from solver.rules.base import *
from forms.abc import *
from core.classes import zero, one


rules = RewriteGroup((
    RewriteSet(( # TODO generalised version
        a1**a2 * a1**a3,
        a1 ** (a2+a3)
    )),
    RewriteSet((
        a1**a2 / a1**a3,
        a1 ** (a2-a3)
    )),
    RewriteSet(( # TODO generalised version
        a1**a3 * a2**a3,
        (a1*a2) ** a3
    )),
    RewriteSet((
        a1**a3 / a2**a3,
        (a1/a2) ** a3
    )),
    RewriteSet((
        (a1**a2) ** a3,
        a1 ** (a2*a3)
    )),
    RewriteRule(
        form=a1**a2,
        target=one / a1**-a2
    ),
    RewriteRule(
        form=one / a1**a2,
        target=a1**-a2
    ),
    RewriteRule(
        form=a1 ** zero,
        target=one
    ),
    RewriteSet((
        a1**one,
        a1
    ))
))


if __name__ == '__main__':
    from core.classes import *
    x = Var('x')
    expr = (x**2+3/x-8*x)**0
    print(expr)
    new = rules.rewrite(expr)
    for i in new:
        print(str(i))