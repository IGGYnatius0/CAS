from math import log

from CAS.core import *
from CAS.core.expr.func import SingleArgInit


class log(Func, SingleArgInit):
    name = 'log'
    func = lambda num: log(evaluate(num))
    n_args = 1



if __name__ == '__main__':
    expr = log(1)
    print(repr(expr))