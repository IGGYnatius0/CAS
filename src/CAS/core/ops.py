from functools import singledispatch
from itertools import product

from .expr import *
from .simplify import decomp, simplify_decomp


__all__ = ['expand', 'factorize', 'substitute_vars', 'evaluate', 'group_nums']


##########
# EXPAND #
##########


@singledispatch
def expand(expr):
    return expr


@expand.register(Sum)
def _(sum):
    return Sum([expand(term) for term in sum.terms])


@expand.register(Prod)
def _(prod):
    to_expand = []
    for factor in prod.factors:
        factor = expand(factor)
        if isinstance(factor, Sum):
            to_expand.append(factor.terms)
        else:
            to_expand.append([factor])
    return Sum([Prod(term) for term in product(*to_expand)])


@expand.register(Frac)
def _(frac):
    return Frac(expand(frac.numer), expand(frac.denom))


@expand.register(Exp)
def _(exp):
    if isinstance(exp.power, Num) and exp.power > 0:
        return expand(Prod([exp.base] * exp.power.value))
    return exp


@expand.register(Eqn)
def _(eqn):
    return Eqn(expand(eqn.lhs), expand(eqn.rhs))


@expand.register(Func)
def _(func):
    return type(func)(*[expand(arg) for arg in func.args])


@singledispatch
def factorize(expr):
    return expr


@factorize.register(Prod)
def _(prod):
    return Prod([factorize(factor) for factor in prod.factors])


@factorize.register(Frac)
def _(frac):
    return Frac(factorize(frac.numer), factorize(frac.denom))


@factorize.register(Exp)
def _(exp):
    return Exp(factorize(exp.base), factorize(exp.power))


@factorize.register(Eqn)
def _(eqn):
    return Eqn(factorize(eqn.lhs), factorize(eqn.rhs))


@factorize.register(Sum)
def _(sum):
    decomps = [decomp(term).copy() for term in sum.terms]
    common = decomps[0].copy()
    for d in decomps[1:]:
        common &= d
    common = simplify_decomp(common)
    for i in range(len(decomps)):
        decomps[i].subtract(common)

    common_prod = decomp2prod(common)

    terms_list = []
    for d in decomps:
        temp = []
        for expr, power in d.items():
            if power != 0:
                temp.append(Exp(expr, power))
        terms_list.append(Prod(temp))
    terms_sum = Sum(terms_list)

    return Prod([common_prod, terms_sum])


@singledispatch
def substitute_vars(expr, var_map):
    pass


@substitute_vars.register(Sum)
def _(sum, var_map):
    return Sum([substitute_vars(term, var_map) for term in sum.terms])


@substitute_vars.register(Prod)
def _(prod, var_map):
    return Prod([substitute_vars(factor, var_map) for factor in prod.factors])


@substitute_vars.register(Frac)
def _(frac, var_map):
    return Frac(substitute_vars(frac.numer, var_map), substitute_vars(frac.denom, var_map))


@substitute_vars.register(Exp)
def _(exp, var_map):
    return Exp(substitute_vars(exp.base, var_map), substitute_vars(exp.power, var_map))


def evaluate(expr):
    if not expr.isnum:
        raise RuntimeError("Cannot evaluate non isnum expression")
    return _evaluate(expr)


@singledispatch
def _evaluate(expr):
    return expr


@_evaluate.register(Sum)
def _(sum):
    return sum([_evaluate(term) for term in sum.terms])


@_evaluate.register(Prod)
def _(prod):
    num = 1
    for factor in prod.factors:
        num *= _evaluate(factor)
    return num

@_evaluate.register(Frac)
def _(frac):
    return _evaluate(frac.numer) / _evaluate(frac.denom)


@_evaluate.register(Exp)
def _(exp):
    return _evaluate(exp.base) ** _evaluate(exp.power)


@singledispatch
def group_nums(expr):
    return expr


@group_nums.register(Sum)
def _(sum):
    terms = [group_nums(term) for term in sum.terms]
    temp = Sum(terms)
    if temp.isnum:
        return temp
    nums = []
    for i, term in reversed(list(enumerate(terms))):
        if term.isnum:
            nums.append(terms.pop(i))
    sum_ = Sum(terms)
    if len(nums) == 1:
        sum_.terms.append(nums[0])
    elif len(nums) > 1:
        sum_.terms.append(Sum(nums))
    return sum_


@group_nums.register(Prod)
def _(prod):
    factors = [group_nums(factor) for factor in prod.factors]
    temp = Prod(factors)
    if temp.isnum:
        return temp
    nums = []
    for i, factor in reversed(list(enumerate(factors))):
        if factor.isnum:
            nums.append(factors.pop(i))
    prod = Prod(factors)
    if len(nums) == 1:
        prod.factors.append(nums[0])
    elif len(nums) > 1:
        prod.factors.append(Prod(nums))
    return prod


@group_nums.register(Frac)
def _(frac):
    return Frac(group_nums(frac.numer), group_nums(frac.denom))


@group_nums.register(Exp)
def _(exp):
    return Exp(group_nums(exp.base), group_nums(exp.power))
