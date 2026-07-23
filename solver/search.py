from core.classes import *
from rewrite import rewrite
from solver import RULES


def iterative_deepening_inner(eqn, seen, max_depth, current_depth):
    solns = RULES.apply(eqn)
    if solns:
        return solns
    if current_depth == max_depth:
        return None
    new_eqns = rewrite(eqn)
    for i, new_eqn in reversed(tuple(enumerate(new_eqns))):
        if new_eqn in seen:
            new_eqns.pop(i)
    seen.update(new_eqns)
    for new_eqn in new_eqns:
        solns = iterative_deepening_inner(new_eqn, seen, max_depth, current_depth + 1)
        if solns:
            return solns
    return None


def iterative_deepening(eqn, max_depth=6):
    for i in range(1, max_depth + 1):
        print(f'depth {i}')
        seen = set()
        solns = iterative_deepening_inner(eqn, seen, i, 0)
        print(len(seen))
        if solns:
            return solns
    return None


if __name__ == '__main__':
    x = Var('x')
    eqn = Eqn(2*x+3, x-5)
    solns = iterative_deepening(eqn)
    for soln in solns:
        print(soln)