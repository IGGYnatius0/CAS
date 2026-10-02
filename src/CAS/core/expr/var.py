from functools import cached_property

from .registry import EXPRS
from .base import CoreVarBase
from CAS.exceptions import InvalidSubroutineError


class Var(CoreVarBase):
    def __init__(self, symbol):
        self.sym = symbol

    @cached_property
    def get_vars(self):
        return {self}

    @cached_property
    def isnum(self):
        return False

    def copy(self):
        return self # Can do this because strings are immutable

    def apply(self, func, *args, to_list=False):
        raise InvalidSubroutineError("Cannot use .apply method on Var")


EXPRS.var = Var