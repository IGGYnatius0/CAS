from solver.rules.base import *
from forms.abc import *
from core.classes import *


def prod_fracs_rewrite(expr):
    if not isinstance(expr, Prod):
        return []
    if len(expr.factors) < 2:
        return []
    for factor in expr.factors:
        if not isinstance(factor, Frac):
            return []
    numer = Prod([factor.numer for factor in expr.factors])
    denom = Prod([factor.denom for factor in expr.factors])
    output = Frac(numer, denom)
    return [output]


def sum_fracs_rewrite(expr):
    if not isinstance(expr, Sum):
        return []
    if len(expr.terms) < 2:
        return []
    for term in expr.terms:
        if not isinstance(term, Frac):
            return []
    numer = []
    for i in range(len(expr.terms)):
        factors = []
        for j, term in enumerate(expr.terms):
            if i == j:
                factors.append(term.numer)
            else:
                factors.append(term.denom)
        numer.append(Prod(factors))
    denom = Prod([term.denom for term in expr.terms])
    output = Frac(Sum(numer), denom)
    return [output]


prod_fracs = RewriteRule()
sum_fracs = RewriteRule()
prod_fracs.rewrite = prod_fracs_rewrite
sum_fracs.rewrite = sum_fracs_rewrite


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

    prod_fracs,

    sum_fracs,

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
    from core.abc import a, b, c, d, e, f, g, h
    expr = (a/b)*(c/d)*(e/f)*(g/h)
    print(expr)
    new = prod_fracs_rewrite(expr)
    for i in new:
        print(i)