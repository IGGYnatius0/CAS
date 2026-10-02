from functools import singledispatch

from .expr import *
from CAS.exceptions import InvalidSubroutineError


__all__ = ['isrational']


@singledispatch
def isrational(expr):
    pass


@isrational.register(Num)
def _(num):
    return True


@isrational.register(Var)
def _(var):
    return False


@isrational.register(Sum)
@isrational.register(Prod)
@isrational.register(Frac)
def _(expr):
    return all(expr.apply(isrational, to_list=True))


@isrational.register(Exp)
def _(expr):
    return isinstance(expr.base, Num) and expr.base > 0 and isinstance(expr.power, Num)


@isrational.register(Eqn)
def _(eqn):
    raise InvalidSubroutineError("Cannot use isrational function on Eqn")


@isrational.register(Func)
def _(func):
    return False