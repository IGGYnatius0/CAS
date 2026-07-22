from rewrite.expr_rules.base import RewriteGroup
from rewrite.expr_rules.exponents import rules as exp_rules
from rewrite.expr_rules.fractions import rules as frac_rules
from rewrite.expr_rules.algebra import rules as alg_rules


__all__ = ['RULES']


RULES = RewriteGroup((
    alg_rules,
    exp_rules,
    frac_rules,
))