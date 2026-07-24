from core.classes import *
from polynomial import *


# Cubic, quartic, integer factoring


if __name__ == '__main__':
    y = Var('y')
    for root in get_rational_roots([Num(8), 1, 1, Num(-6)]):
        print(root)