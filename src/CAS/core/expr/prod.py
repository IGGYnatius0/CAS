from collections import Counter
from functools import cached_property
from itertools import product

from .registry import EXPRS
from .base import CoreProdBase
from .utils import *


class Prod(CoreProdBase):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if isinstance(factor, EXPRS.prod):
                self.factors.extend(factor.factors)
            else:
                self.factors.append(make_expr(factor))
        if not self.factors:
            self.factors = [EXPRS.one]

    # def decomp(self):
    #     c = Counter()
    #     for factor in self.factors:
    #         c.update(factor.decomp())
    #     c = simplify_decomp(c)
    #     return c

    def expand(self):
        to_expand = []
        for factor in self.factors:
            factor = factor.expand()
            if isinstance(factor, EXPRS.sum):
                to_expand.append(factor.terms)
            else:
                to_expand.append([factor])
        return EXPRS.sum([Prod(term) for term in product(*to_expand)])

    def factorize(self):
        return Prod([factor.factorize() for factor in self.factors])

    # def simplify(self):
    #     """Simplifies the expression; if factors contain 0, returns 0"""
    #     if len(self.factors) == 1:
    #         return self.factors[0].simplify()
    #     decomp = Prod([factor.simplify() for factor in self.factors]).decomp()
    #     numer = 1
    #     denom = 1
    #     factors = [] # non rational stuff
    #     for base, power in decomp.items():
    #         if isinstance(base, EXPRS.num) and isinstance(power, EXPRS.num):
    #             if power > 0:
    #                 numer *= base.value ** power.value
    #             elif power < 0:
    #                 denom *= base.value ** -power.value
    #         else:
    #             factors.append(EXPRS.exp(base, power).simplify())
    #     # DO NOT use Frac(numer, denom).simplify() as that uses Prod simplify,
    #     # which will cause RecursionError
    #     if numer == 0:
    #         return EXPRS.zero
    #     if denom == 0:
    #         raise ZeroDivisionError(f'{numer=}; {denom=}; {factors=}')
    #
    #     if numer == 1 and denom != 1:
    #         const = EXPRS.exp(denom, -1)
    #     elif numer != 1 and denom == 1:
    #         const = EXPRS.num(numer)
    #     elif numer == 1 and denom == 1:
    #         const = EXPRS.one
    #     else:
    #         const = Prod([numer, EXPRS.exp(denom, -1)])
    #
    #     if len(factors) == 0:
    #         return const
    #     if const == 1 and len(factors) == 1:
    #         return factors[0]
    #     if const == 1 and len(factors) > 1:
    #         return Prod(factors)
    #     return const * Prod(factors)

    def substitute_vars(self, var_map):
        return Prod([term.substitute_vars(var_map) for term in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    @cached_property
    def isnum(self):
        for factor in self.factors:
            if not factor.isnum:
                return False
        return True

    def eval_nums(self):
        super().eval_nums()
        num = 1
        for factor in self.factors:
            num *= factor.eval_nums()
        return num

    def copy(self):
        return Prod([factor.copy() for factor in self.factors])

    def group_nums(self):
        factors = [factor.group_nums() for factor in self.factors]
        temp = Prod(factors)
        if temp.isnum:
            return temp
        nums = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isnum:
                nums.append(factors.pop(i))
        prod = Prod(factors)
        if len(nums) == 1:
            prod.factors.append(nums[0])
        elif len(nums) > 1:
            prod.factors.append(Prod(nums))
        return prod


EXPRS.prod = Prod