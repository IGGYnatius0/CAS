from collections import Counter
from functools import cached_property

from .registry import EXPRS
from .base import CoreExpBase
from .utils import make_expr # , simplify_decomp
from CAS.core.pfactor import pfactor


class Exp(CoreExpBase):
    def __init__(self, base, power):
        self.base = make_expr(base)
        self.power = make_expr(power)

    def substitute_vars(self, var_map):
        return self.base.substitute_vars(var_map) ** self.power.substitute_vars(var_map)

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    @cached_property
    def isnum(self):
        return self.base.isnum and self.power.isnum

    def eval_nums(self):
        super().eval_nums()
        return self.base.eval_nums() ** self.power.eval_nums()

    def copy(self):
        return Exp(self.base.copy(), self.power.copy())

    def group_nums(self):
        return Exp(self.base.group_nums(), self.power.group_nums())


EXPRS.exp = Exp