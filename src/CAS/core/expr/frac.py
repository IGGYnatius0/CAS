from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseFrac
from .utils import *


@EXPRS.register('frac')
class Frac(CoreBaseFrac):
    def __init__(self, numer, denom):
        self.numer = clean_num(numer) if is_ext_num(numer) else numer
        self.denom = clean_num(denom) if is_ext_num(denom) else denom

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        numers = self.numer.decomp()
        denoms = self.denom.decomp()
        numers.subtract(denoms)
        return numers

    def expand(self):
        return EXPRS.frac(self.numer.expand(), self.denom.expand())

    def factorize(self):
        return EXPRS.frac(self.numer.factorize(), self.denom.factorize())

    def simplify(self):
        """Returns the fraction with simplified numerator and denominator"""
        numer = self.numer.simplify().decomp()
        denom = self.denom.simplify().decomp()
        numer.subtract(denom)
        return decomp2prod(numer).simplify()

    def substitute_vars(self, var_map):
        return EXPRS.frac(self.numer.substitute_vars(var_map),
                    self.denom.substitute_vars(var_map))

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    @cached_property
    def isnum(self):
        return self.numer.isnum and self.denom.isnum

    def copy(self):
        return EXPRS.frac(self.numer.copy(), self.denom.copy())

    def eval_nums(self):
        return self.numer.eval_nums() / self.denom.eval_nums()

    def group_nums(self):
        return EXPRS.frac(self.numer.group_nums(), self.denom.group_nums())