from functools import singledispatch
from CAS.core import *


__all__ = ['isrational']


@singledispatch
def isrational(expr):
    return False


@isrational.register(Num)
def _(expr):
    return True


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
    return isinstance(expr.base, Num) and expr.base > 0 and isinstance(expr.power, Num)