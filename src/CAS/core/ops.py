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
    pass


@expand.register(Num)
@expand.register(Var)
def _(expr):
    return expr


@expand.register(Sum)
@expand.register(Frac)
@expand.register(Exp)
@expand.register(Func)
@expand.register(Eqn)
def _(expr):
    return expr.apply(expand)


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


#############
# FACTORIZE #
#############


@singledispatch
def factorize(expr):
    pass


@factorize.register(Num)
@factorize.register(Var)
def _(expr):
    return expr


@factorize.register(Prod)
@factorize.register(Frac)
@factorize.register(Exp)
@factorize.register(Func)
@factorize.register(Eqn)
def _(expr):
    return expr.apply(factorize)


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


###################
# SUBSTITUTE_VARS #
###################


@singledispatch
def substitute_vars(expr, var_map):
    pass


@substitute_vars.register(Num)
def _(num, var_map):
    return num


@substitute_vars.register(Var)
def _(var, var_map):
    if var in var_map:
        return var_map[var]
    return var


@substitute_vars.register(Sum)
@substitute_vars.register(Prod)
@substitute_vars.register(Frac)
@substitute_vars.register(Exp)
@substitute_vars.register(Func)
@substitute_vars.register(Eqn)
def _(expr, var_map):
    return expr.apply(substitute_vars, var_map)


############
# EVALUATE #
############


def evaluate(expr):
    if not expr.isnum:
        raise RuntimeError("Cannot evaluate non isnum expression")
    return _evaluate(expr)


@singledispatch
def _evaluate(expr):
    pass


@_evaluate.register(Num)
# No need Var because isnum ensures there is no Var
def _(expr):
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


# TODO Eqn and Func


##############
# GROUP_NUMS #
##############


@singledispatch
def group_nums(expr):
    pass


@group_nums.register(Num)
@group_nums.register(Var)
def _(expr):
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
@group_nums.register(Exp)
@group_nums.register(Func)
@group_nums.register(Eqn)
def _(expr):
    return expr.apply(group_nums)