from functools import singledispatch

from .expr import *
from CAS.core import *


#############
# core2form #
#############


@singledispatch
def core2form(expr):
    pass

@core2form.register(Num)
def _(expr):
    return FormNum(expr.value)

@core2form.register(Var)
def _(expr):
    return FormVar(expr.sym)

@core2form.register(Sum)
def _(expr):
    return FormSum([core2form(term) for term in expr.terms])

@core2form.register(Prod)
def _(expr):
    return FormProd([core2form(factor) for factor in expr.factors])

@core2form.register(Frac)
def _(expr):
    return FormFrac(core2form(expr.numer), core2form(expr.denom))

@core2form.register(Exp)
def _(expr):
    return FormExp(core2form(expr.base), core2form(expr.power))

@core2form.register(Eqn)
def _(expr):
    return FormEqn(core2form(expr.lhs), core2form(expr.rhs))


def form2core(form):
    pass


def substitute_consts(form):
    pass


def group_consts(form):
    pass