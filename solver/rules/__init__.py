from .base import RewriteGroup
from .exponents import rules as exp_rules
from .fractions import rules as frac_rules


__all__ = ['RULES']


RULES = RewriteGroup((
    exp_rules,
    frac_rules
))