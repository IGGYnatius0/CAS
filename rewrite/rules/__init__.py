from rewrite.rules.base import RewriteGroup
from rewrite.rules.exponents import rules as exp_rules
from rewrite.rules.fractions import rules as frac_rules
from rewrite.rules.algebra import rules as alg_rules


__all__ = ['RULES']


RULES = RewriteGroup((
    exp_rules,
    frac_rules,
    alg_rules
))