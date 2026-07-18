from solver.rules.base import RewriteGroup
from solver.rules.exponents import rules as exp_rules
from solver.rules.fractions import rules as frac_rules
from solver.rules.algebra import rules as alg_rules


__all__ = ['RULES']


RULES = RewriteGroup((
    exp_rules,
    frac_rules,
    alg_rules
))