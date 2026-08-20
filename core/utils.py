from functools import singledispatch
from core.classes import *


__all__ = ['isrational']


@singledispatch
def isrational(expr):
    return False


@isrational.register
def _(expr: Num):
    return int(expr) == expr


@isrational.register
def _(expr: Sum):
    return all(isrational(term) for term in expr.terms)


@isrational.register
def _(expr: Prod):
    return all(isrational(factor) for factor in expr.factors)


@isrational.register
def _(expr: Frac):
    return isrational(expr.numer) and isrational(expr.denom)


@isrational.register
def _(expr: Exp):
    return int(expr.base) == expr.base and int(expr.power) == expr.power