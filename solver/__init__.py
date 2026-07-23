from solver.base import SolveGroup
from solver.polynomial import rules as poly_rules


__all__ = ['RULES']


RULES = SolveGroup((
    poly_rules,
))