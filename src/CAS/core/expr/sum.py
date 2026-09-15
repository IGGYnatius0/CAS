from collections import defaultdict
from functools import cached_property

from .registry import EXPRS
from .base import CoreSumBase
from .utils import *


class Sum(CoreSumBase):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if isinstance(term, EXPRS.sum):
                self.terms.extend(term.terms)
            else:
                self.terms.append(make_expr(term))
        if not self.terms:
            self.terms = [EXPRS.zero]

    def expand(self):
        return Sum([term.expand() for term in self.terms])

    def factorize(self):
        decomps = [term.factorize().decomp() for term in self.terms]
        common = decomps[0].copy()
        for decomp in decomps[1:]:
            common &= decomp
        for i in range(len(decomps)):
            decomps[i].subtract(common)

        common_prod = decomp2prod(common)

        terms_list = []
        for decomp in decomps:
            temp = []
            for expr, power in decomp.items():
                if power != 0:
                    temp.append(EXPRS.exp(expr, power))
            terms_list.append(EXPRS.prod(temp))
        terms_sum = Sum(terms_list)

        return EXPRS.prod([common_prod, terms_sum])

    @staticmethod
    def _sum_nums(exprs):
        const = 0
        terms = []
        for expr in exprs:
            expr = expr.simplify()
            if isinstance(expr, EXPRS.num):
                const += expr.value
            else:
                terms.append(expr)
        if len(terms) == 0:
            return EXPRS.num(const)
        if const == 0:
            return Sum(terms)
        terms.append(const)
        return Sum(terms)

    @staticmethod
    def _sum_coeffs(coeffs: list[list[EXPRS.exp]]):
        # This method is as complicated as it is because the combining of
        # Nums either by addition or multiplication requires the separation
        # of Nums and expressions that are isnum. Only after they are
        # separated can the combining happen via .value .

        # Sort expressions into numer and denom, numeric and symbolic
        numers = []
        denoms = []
        for coeff in coeffs:
            numer_num = 1
            denom_num = 1
            numer_exprs = []
            denom_exprs = []
            for exp in coeff:
                if isinstance(exp.power, EXPRS.num) and exp.power < 0:
                    if isinstance(exp.base, EXPRS.num):
                        denom_num *= exp.base.value ** -exp.power.value
                    else:
                        denom_exprs.append(exp)
                else:
                    if isinstance(exp.base, EXPRS.num) and isinstance(exp.power, EXPRS.num):
                        numer_num *= exp.base.value ** exp.power.value
                    else:
                        numer_exprs.append(exp)
            numer_exprs.append(numer_num)
            denom_exprs.append(denom_num)
            numers.append(EXPRS.prod(numer_exprs))
            denoms.append(EXPRS.prod(denom_exprs))

        # Sum of fractions
        numer = []
        denom = []
        for i, n in enumerate(numers):
            temp = []
            for j, d in enumerate(denoms):
                if i == j:
                    temp.append(n)
                    denom.append(d)
                else:
                    temp.append(d)
            numer.append(EXPRS.prod(temp))
        return EXPRS.frac(Sum._sum_nums(numer), EXPRS.prod(denom)).simplify()

    def simplify(self):
        if len(self.terms) == 1:
            return self.terms[0].simplify()
        decomps = [term.simplify().decomp() for term in self.terms]
        terms_dict = defaultdict(list)
        for decomp in decomps:
            coeff = []
            factors = []
            for base, power in decomp.items():
                # Separate coefficients and variables
                expr = EXPRS.exp(base, power)
                if base.isnum and power.isnum:
                    coeff.append(expr)
                else:
                    factors.append(expr.simplify())
            terms_dict[EXPRS.prod(factors)].append(coeff)

        # Sum coefficients together
        terms = []
        for factors, coeffs in terms_dict.items():
            term = (self._sum_coeffs(coeffs) * factors).simplify()
            if term != 0:
                terms.append(term)
        if len(terms) == 0:
            return 0
        if len(terms) == 1:
            return terms[0]
        return Sum(terms)

    def substitute_vars(self, var_map):
        return EXPRS.sum([term.substitute_vars(var_map) for term in self.terms])

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])

    @cached_property
    def isnum(self):
        for term in self.terms:
            if not term.isnum:
                return False
        return True

    def eval_nums(self):
        super().eval_nums()
        return sum([term.eval_nums() for term in self.terms])

    def copy(self):
        return EXPRS.sum([term.copy() for term in self.terms])

    def group_nums(self):
        terms = [term.group_nums() for term in self.terms]
        temp = EXPRS.sum(terms)
        if temp.isnum:
            return temp
        nums = []
        for i, term in reversed(list(enumerate(terms))):
            if term.isnum:
                nums.append(terms.pop(i))
        sum_ = EXPRS.sum(terms)
        if len(nums) == 1:
            sum_.terms.append(nums[0])
        elif len(nums) > 1:
            sum_.terms.append(EXPRS.sum(nums))
        return sum_


EXPRS.sum = Sum