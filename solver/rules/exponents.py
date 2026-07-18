from solver.rules.base import *
from forms.abc import *
from core.classes import zero, one


def sum_pows_rewrite_1(expr):
    if not isinstance(expr, Prod):
        return []
    if len(expr.factors) < 2:
        return []
    for factor in expr.factors:
        if not isinstance(factor, Exp):
            return []
        if factor.base != expr.factors[0].base:
            return []
    powers = [factor.power for factor in expr.factors]
    output = expr.factors[0].base ** Sum(powers)
    return [output]


def sum_pows_rewrite_2(expr):
    if not isinstance(expr, Exp):
        return []
    if not isinstance(expr.power, Sum):
        return []
    if len(expr.power.terms) < 2:
        return []
    output = Prod([Exp(expr.base, term) for term in expr.power.terms])
    return [output]


def prod_bases_rewrite_1(expr):
    if not isinstance(expr, Prod):
        return []
    if len(expr.factors) < 2:
        return []
    for factor in expr.factors:
        if not isinstance(factor, Exp):
            return []
        if factor.power != expr.factors[0].power:
            return []
    bases = [factor.base for factor in expr.factors]
    output = Prod(bases) ** expr.factors[0].power
    return [output]


def prod_bases_rewrite_2(expr):
    if not isinstance(expr, Exp):
        return []
    if not isinstance(expr.base, Prod):
        return []
    if len(expr.base.factors) < 2:
        return []
    output = Prod([Exp(base, expr.power) for base in expr.base.factors])
    return [output]


def sum_pows_rewrite(expr):
    return sum_pows_rewrite_1(expr) + sum_pows_rewrite_2(expr)


def prod_bases_rewrite(expr):
    return prod_bases_rewrite_1(expr) + prod_bases_rewrite_2(expr)


sum_pows = RewriteRule()
prod_bases = RewriteRule()
sum_pows.rewrite = sum_pows_rewrite
prod_bases.rewrite = prod_bases_rewrite


rules = RewriteGroup((
    sum_pows,

    RewriteSet((
        a1**a2 / a1**a3,
        a1 ** (a2-a3)
    )),

    prod_bases,

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
        form=a1**zero,
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
    expr = x**3*x**2*x**-4
    print(expr)
    new = rules.rewrite(expr)
    for i in new:
        print(str(i))