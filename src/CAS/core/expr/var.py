from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseVar


@EXPRS.register('var')
class Var(CoreBaseVar):
    def __init__(self, symbol):
        self.sym = symbol

    def substitute_vars(self, var_map):
        if self in var_map:
            return var_map[self]
        return self

    @cached_property
    def get_vars(self):
        return {self}

    @cached_property
    def isnum(self):
        return False

    def copy(self):
        return EXPRS['var'](self.sym)