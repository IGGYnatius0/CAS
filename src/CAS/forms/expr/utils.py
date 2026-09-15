from decimal import Decimal
from functools import singledispatch

from .registry import FORMS
from .base import FormExprBase
from CAS.core.expr import *


__all__ = ['make_form', 'core2form', 'form2core']


def make_formnum(num):
    if isinstance(num, Num):
        return FORMS.num(num.value)
    if not hasattr(num, 'as_integer_ratio'):
        raise ValueError(f"Input of type '{type(num)}' cannot be converted to FormNum")
    ratio = Decimal(str(num)).as_integer_ratio()
    if ratio[1] == 1:
        return FORMS.num(int(num))
    return FORMS.frac(*ratio)


def make_form(expr):
    try:
        return make_formnum(expr)
    except ValueError:
        if isinstance(expr, FormExprBase):
            return expr
        raise ValueError("Input expression must inherit from FormExprBase")


#############
# core2form #
#############


@singledispatch
def core2form(expr):
    pass

@core2form.register(Num)
def _(expr):
    return FORMS.num(expr)

@core2form.register(Var)
def _(expr):
    return FORMS.var(expr.sym)

@core2form.register(Sum)
def _(expr):
    return FORMS.sum([core2form(term) for term in expr.terms])

@core2form.register(Prod)
def _(expr):
    return FORMS.prod([core2form(factor) for factor in expr.factors])

@core2form.register(Frac)
def _(expr):
    return FORMS.frac(core2form(expr.numer), core2form(expr.denom))

@core2form.register(Exp)
def _(expr):
    return FORMS.exp(core2form(expr.base), core2form(expr.power))

@core2form.register(Eqn)
def _(expr):
    return FORMS.eqn(core2form(expr.lhs), core2form(expr.rhs))


#############
# form2core #
#############

def form2core(form, var_map={}, const_map={}):
    if isinstance(form, FORMS.num):
        return Num(form.value)
    if isinstance(form, FORMS.const):
        if form not in const_map:
            raise RuntimeError("'const_map' does not contain all constants")
        return const_map[form]
    if isinstance(form, (FORMS.var, FORMS.wild)):
        if not var_map:
            return Var(form.sym)
        if form not in var_map:
            raise RuntimeError("'var_map' does not contain all variables")
        return var_map[form]
    if isinstance(form, FORMS.sum):
        return Sum([form2core(term, var_map, const_map) for term in form.terms])
    if isinstance(form, FORMS.prod):
        return Prod([form2core(factor, var_map, const_map) for factor in form.factors])
    if isinstance(form, FORMS.frac):
        return Frac(form2core(form.numer, var_map, const_map),
                    form2core(form.denom, var_map, const_map))
    if isinstance(form, FORMS.exp):
        return Exp(form2core(form.base, var_map, const_map),
                   form2core(form.power, var_map, const_map))
    if isinstance(form, FORMS.eqn):
        return Eqn(form2core(form.lhs, var_map, const_map),
                   form2core(form.rhs, var_map, const_map))