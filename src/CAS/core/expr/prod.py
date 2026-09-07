from collections import Counter
from functools import cached_property
from itertools import product

from .registry import EXPRS
from .base import CoreBaseExpr, CoreBaseProd
from .utils import *


@EXPRS.register('prod')
class Prod(CoreBaseProd):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if is_ext_num(factor):
                self.factors.append(clean_num(factor))
            elif isinstance(factor, EXPRS.sum):
                self.factors.extend(factor.factors)
            elif isinstance(factor, CoreBaseExpr):
                self.factors.append(factor)
            else:
                raise ValueError("Factors must be core exprs or Python numbers")
        if not self.factors:
            self.factors = [EXPRS.num(0)]

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        c = Counter()
        for factor in self.factors:
            c.update(factor.decomp())
        return c

    def expand(self):
        to_expand = []
        for factor in self.factors:
            factor = factor.expand()
            if isinstance(factor, EXPRS.sum):
                to_expand.append(factor.terms)
            else:
                to_expand.append([factor])
        return EXPRS.sum([EXPRS.prod(term) for term in product(*to_expand)])

    def factorize(self):
        return EXPRS.prod([factor.factorize() for factor in self.factors])

    def simplify(self):
        """Simplifies the expression; if factors contain 0, returns 0"""
        decomp = EXPRS.prod([factor.simplify() for factor in self.factors]).decomp()
        const = 1
        factors = []
        for base, power in decomp.items():
            expr = EXPRS.exp(base, power).simplify()
            if isinstance(expr, EXPRS.num):
                const *= expr
            else:
                factors.append(expr)
        if const == 0:
            return 0
        if len(factors) == 0:
            return const
        if const == 1 and len(factors) == 1:
            return factors[0]
        if const == 1 and len(factors) > 1:
            return EXPRS.prod(factors)
        return const * EXPRS.prod(factors)

    def substitute_vars(self, var_map):
        return EXPRS.prod([term.substitute_vars(var_map) for term in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    @cached_property
    def isnum(self):
        for factor in self.factors:
            if not factor.isnum:
                return False
        return True

    def copy(self):
        return EXPRS.prod([factor.copy() for factor in self.factors])

    def eval_nums(self):
        num = 1
        factors = []
        has_num = False
        for factor in self.factors:
            if factor.isnum:
                num += factor.eval_nums()
                has_num = True
            else:
                factors.append(factor)
        if has_num:
            if len(factors) > 0:
                return EXPRS.prod(factors + [num])
            return num
        return EXPRS.prod(factors)

    def group_nums(self):
        factors = [factor.group_nums() for factor in self.factors]
        temp = EXPRS.prod(factors)
        if temp.isnum:
            return temp
        nums = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isnum:
                nums.append(factors.pop(i))
        prod = EXPRS.prod(factors)
        if len(nums) == 1:
            prod.factors.append(nums[0])
        elif len(nums) > 1:
            prod.factors.append(EXPRS.prod(nums))
        return prod