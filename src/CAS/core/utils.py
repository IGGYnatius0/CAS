from functools import singledispatch
from CAS.core.expr import *


__all__ = ['isrational']


@singledispatch
def isrational(expr):
    return False


@isrational.register(Num)
def _(expr):
    return int(expr) == expr


@isrational.register(Sum)
def _(expr):
    return all(isrational(term) for term in expr.terms)


@isrational.register(Prod)
def _(expr):
    return all(isrational(factor) for factor in expr.factors)


@isrational.register(Frac)
def _(expr):
    return isrational(expr.numer) and isrational(expr.denom)


@isrational.register(Exp)
def _(expr):
    return int(expr.base) == expr.base and int(expr.power) == expr.power