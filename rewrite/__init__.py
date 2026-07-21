from core.classes import *
from rewrite.expr import rewrite as expr_rewrite
from rewrite.eqn import rewrite as eqn_rewrite


def rewrite(eqn):
    new_eqns = []
    new_eqns.extend(eqn_rewrite(eqn))
    new_lhs = expr_rewrite(eqn.lhs)
    new_rhs = expr_rewrite(eqn.rhs)
    new_eqns.extend([Eqn(lhs, eqn.rhs) for lhs in new_lhs])
    new_eqns.extend([Eqn(eqn.lhs, rhs) for rhs in new_rhs])
    return list(dict.fromkeys(new_eqns))