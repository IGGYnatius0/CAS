from collections import defaultdict
from functools import cached_property

from .registry import EXPRS
from .base import CoreBaseExpr, CoreBaseSum
from .utils import *


@EXPRS.register('sum')
class Sum(CoreBaseSum):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if is_ext_num(term):
                self.terms.append(clean_num(term))
            elif isinstance(term, EXPRS.sum):
                self.terms.extend(term.terms)
            elif isinstance(term, CoreBaseExpr):
                self.terms.append(term)
            else:
                raise ValueError("Terms must be core exprs or Python numbers")
        if not self.terms:
            self.terms = [EXPRS.num(0)]

    def expand(self):
        return Sum([term.expand() for term in self.terms])

    def factorize(self):
        decomps = [term.factorize().decomp() for term in self.terms]
        common = decomps[0].copy()
        for decomp in decomps[1:]:
            common &= decomp
        for i in range(len(decomps)):
            decomps[i].subtract(common)

        # Convert from Counter to list of EXPRS['exp']
        common_list = []
        for expr, power in common.items():
            common_list.append(EXPRS['exp'](expr, power))
        common_prod = EXPRS['prod'](common_list)

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
    def sum_fracs(fracs):
        numer = 0
        denom = 1
        for i, (_, d) in enumerate(fracs):
            temp = 1
            for j, frac in enumerate(fracs):
                if i == j:
                    temp *= frac[0]
                else:
                    temp *= frac[1]
            numer += temp
            denom *= d
        return EXPRS.frac(numer, denom).simplify()

    def simplify(self): # TODO remove 0
        decomps = [term.simplify().decomp() for term in self.terms]
        terms_dict = defaultdict(list)
        for decomp in decomps:
            numer = 1
            denom = 1
            factors = []
            for base, power in decomp.items():
                if isinstance(base, EXPRS['num']) and isinstance(power, EXPRS['num']) and int(
                        base) == base and int(power) == power:
                    if power < 0:
                        denom *= base ** -power
                    else:
                        numer *= base ** power
                else:
                    factors.append(EXPRS.exp(base, power))
            terms_dict[EXPRS.prod(factors).simplify()].append((numer, denom))
        terms = [(factors * self.sum_fracs(fracs)).simplify() for factors, fracs in terms_dict.items()]
        terms = [term for term in terms if term != 0]
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

    def copy(self):
        return EXPRS.sum([term.copy() for term in self.terms])

    def eval_nums(self):
        num = 0
        terms = []
        has_num = False
        for term in self.terms:
            if term.isnum:
                num += term.eval_nums()
                has_num = True
            else:
                terms.append(term)
        if has_num:
            if len(terms) > 0:
                return EXPRS.sum(terms + [num])
            return num
        return EXPRS.sum(terms)

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