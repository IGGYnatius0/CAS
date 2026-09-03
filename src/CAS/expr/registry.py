from CAS.registry import *


__all__ = ['EXPRS']


EXPRS = Registry()


# Num = None
# Var = None
# Sum = None
# Prod = None
# Frac = None
# Exp = None
#
#
# def load_registry():
#     global Num
#     global Var
#     global Sum
#     global Prod
#     global Frac
#     global Exp
#     Num = EXPRS['num']
#     Var = EXPRS['var']
#     Sum = EXPRS['sum']
#     Prod = EXPRS['prod']
#     Frac = EXPRS['frac']
#     Exp = EXPRS['exp']


# def make_var(sym):
#     return EXPRS['var'](sym)
#
#
# def make_sum(terms):
#     return EXPRS['sum'](terms)
#
#
# def make_prod(factors):
#     return EXPRS['prod'](factors)
#
#
# def make_frac(numer, denom):
#     return EXPRS['frac'](numer, denom)
#
#
# def make_exp(base, power):
#     return EXPRS['exp'](base, power)