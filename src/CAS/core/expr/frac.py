from functools import cached_property

from .registry import EXPRS
from .base import CoreFracBase
from .utils import *


class Frac(CoreFracBase):
    def __init__(self, numer, denom):
        self.numer = make_expr(numer)
        self.denom = make_expr(denom)

    # def decomp(self):
    #     numers = self.numer.decomp()
    #     denoms = self.denom.decomp()
    #     numers.subtract(denoms)
    #     numers = simplify_decomp(numers)
    #     return numers

    def expand(self):
        return EXPRS.frac(self.numer.expand(), self.denom.expand())

    def factorize(self):
        return EXPRS.frac(self.numer.factorize(), self.denom.factorize())

    # def simplify(self):
    #     """Returns the fraction with simplified numerator and denominator"""
    #     numer = self.numer.simplify().decomp()
    #     denom = self.denom.simplify().decomp()
    #     numer.subtract(denom)
    #     numer = simplify_decomp(numer)
    #     return decomp2prod(numer).simplify()

    def substitute_vars(self, var_map):
        return EXPRS.frac(self.numer.substitute_vars(var_map), self.denom.substitute_vars(var_map))

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    @cached_property
    def isnum(self):
        return self.numer.isnum and self.denom.isnum

    def eval_nums(self):
        super().eval_nums()
        return self.numer.eval_nums() / self.denom.eval_nums()

    def copy(self):
        return EXPRS.frac(self.numer.copy(), self.denom.copy())

    def group_nums(self):
        return EXPRS.frac(self.numer.group_nums(), self.denom.group_nums())


EXPRS.frac = Frac