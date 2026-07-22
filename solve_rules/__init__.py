from solve_rules.base import SolveGroup
from solve_rules.polynomial import rules as poly_rules


__all__ = ['RULES']


RULES = SolveGroup((
    poly_rules
))