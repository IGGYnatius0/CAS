from core.classes import *
from forms.classes import *
from forms.known_forms import FORMS
from forms.formulas import FORMULAS


def solve(expr):
    pass


if __name__ == '__main__':
    x = Var('x')
    expr = 6 - 17/x + 12/(x**2)
    print(solve(expr))