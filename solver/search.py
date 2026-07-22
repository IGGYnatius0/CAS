from core.classes import *
from rewrite import rewrite
from solve_rules import RULES


def iterative_deepening_inner(eqn, max_depth, current_depth):
    solns = RULES.apply(eqn)
    if solns:
        return solns
    if current_depth == max_depth:
        return None
    new_eqns = rewrite(eqn)
    for new_eqn in new_eqns:
        solns = iterative_deepening_inner(new_eqn, max_depth, current_depth + 1)
        if solns:
            return solns
    return None


if __name__ == '__main__':
    x = Var('x')
    eqn = Eqn(x+1, 0)
    print(iterative_deepening_inner(eqn, 1, 0))