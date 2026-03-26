from core.core_classes import *
from forms.known_forms import forms
from core.num import zero

def match_form(expr):
    # TODO this
    pass


def extract_muls(expr):
    muls = []
    if isinstance(expr, Sum):
        for term in expr.terms:
            muls.extend(extract_muls(term))
    elif isinstance(expr, Prod):
        for factor in expr.factors:
            muls.extend(extract_muls(factor))
    elif isinstance(expr, Exp):
        power = expr.power
        if isinstance(power, Num):
            if power < 0:
                muls.append(Exp(expr.base, -power))
        elif isinstance(power, Prod):
            neg = False
            for factor in power.factors:
                if isinstance(factor, Num):
                    if factor < 0:
                        neg = not neg
            if neg:
                muls.append(Exp(expr.base, -power))
    return muls


def solve(eqn):
    # TODO this
    """
    Solver tries to solve by making x the subject, but checking for form matches at every step
    """
    expr = (eqn.lhs - eqn.rhs).simplify()
    muls = Prod(extract_muls(expr))
    expr = (expr * muls).expand().simplify()
    print(expr)


if __name__ == '__main__':
    x = Var('x')
    eqn = Eqn((x**3-x)/x+(x**2+2*x-3)**2, (x**2+2*x+1)+(x**2-x-2))
    print(eqn)
    print(solve(eqn))