from math import log as mlog

from CAS.core import *
from CAS.core.expr.func import SingleArgInit


__all__ = ['log']


class log(Func, SingleArgInit):
    name = 'log'
    func = mlog # lambda expr: mlog(evaluate(expr))
    n_args = 1



if __name__ == '__main__':
    expr = log(1)
    print(repr(expr))