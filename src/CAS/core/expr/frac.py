from functools import cached_property

from .registry import EXPRS
from .base import CoreFracBase
from .utils import *


class Frac(CoreFracBase):
    def __init__(self, numer, denom):
        self.numer = make_expr(numer)
        self.denom = make_expr(denom)

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    @cached_property
    def isnum(self):
        return self.numer.isnum and self.denom.isnum

    def copy(self):
        return EXPRS.frac(self.numer.copy(), self.denom.copy())

    def apply(self, func, args):
        return Frac(func(self.numer, *args), func(self.denom, *args))


EXPRS.frac = Frac