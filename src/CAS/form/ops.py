from functools import singledispatch

from .expr import *
from CAS.core import *
from CAS.exceptions import BadFunctionError, MissingVarError, MissingConstError


__all__ = ['core2form', 'form2core', 'substitute_consts', 'group_consts']


#############
# CORE2FORM #
#############


@singledispatch
def core2form(expr):
    raise TypeError(f"Invalid type: {type(expr)}")

@core2form.register(Num)
def _(num):
    return FormNum(num.value)

@core2form.register(Var)
def _(var):
    return FormVar(var.sym)

@core2form.register(Sum)
def _(sum):
    return FormSum(sum.apply(core2form, to_iter=True))

@core2form.register(Prod)
def _(prod):
    return FormProd(prod.apply(core2form, to_iter=True))

@core2form.register(Frac)
def _(frac):
    return FormFrac(*frac.apply(core2form, to_iter=True))

@core2form.register(Exp)
def _(exp):
    return FormExp(*exp.apply(core2form, to_iter=True))

@core2form.register(Eqn)
def _(eqn):
    return FormEqn(*eqn.apply(core2form, to_iter=True))

@core2form.register(Func)
def _(func):
    raise BadFunctionError("Cannot use core2form on Func yet...")


#############
# FORM2CORE #
#############


@singledispatch
def form2core(form, var_map={}, const_map={}):
    raise TypeError(f"Invalid type: {type(form)}")

@form2core.register(FormNum)
def _(num, var_map={}, const_map={}):
    return Num(num.value)

@form2core.register(FormVar)
@form2core.register(FormWild)
def _(form, var_map={}, const_map={}):
    if not var_map:
        return Var(form.sym)
    if form not in var_map:
        raise MissingVarError(f"var_map is missing '{form}'")
    return var_map[form]

@form2core.register(FormConst)
def _(const, var_map={}, const_map={}):
    if const not in const_map:
        raise MissingConstError(f"const_map is missing '{const}'")
    return const_map[const]

@form2core.register(FormSum)
def _(sum, var_map={}, const_map={}):
    return Sum(sum.apply(form2core, args=(var_map, const_map), to_iter=True))

@form2core.register(FormProd)
def _(prod, var_map={}, const_map={}):
    return Prod(prod.apply(form2core, args=(var_map, const_map), to_iter=True))

@form2core.register(FormFrac)
def _(frac, var_map={}, const_map={}):
    return Frac(*frac.apply(form2core, args=(var_map, const_map), to_iter=True))

@form2core.register(FormExp)
def _(exp, var_map={}, const_map={}):
    return Exp(*exp.apply(form2core, args=(var_map, const_map), to_iter=True))

@form2core.register(FormEqn)
def _(eqn, var_map={}, const_map={}):
    return Eqn(*eqn.apply(form2core, args=(var_map, const_map), to_iter=True))


#####################
# SUBSTITUTE_CONSTS #
#####################


@singledispatch
def substitute_consts(form, const_map={}):
    raise TypeError(f"Invalid type: {type(form)}")


@substitute_consts.register(FormNum)
@substitute_consts.register(FormVar)
@substitute_consts.register(FormWild)
def _(form, const_map={}):
    return form


@substitute_consts.register(FormConst)
def _(const, const_map={}):
    if const in const_map:
        return const_map[const]
    return const


@substitute_consts.register(FormSum)
@substitute_consts.register(FormProd)
@substitute_consts.register(FormFrac)
@substitute_consts.register(FormExp)
@substitute_consts.register(FormEqn)
def _(form, const_map={}):
    return form.apply(substitute_consts, args=(const_map,))


def group_consts(form):
    raise TypeError(f"Invalid type: {type(form)}")


