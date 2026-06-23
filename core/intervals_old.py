from core.core_classes import *
from core.num import *


"""
########################################################################################################################
##                                                                                                                    ##
##                                           READ BEFORE PROCEEDING!!!                                                ##
##                                                                                                                    ##
########################################################################################################################

For future reference when I come back from bookout and I cannot remember anything here:
- Change Intervals constructor to use Bound objects instead of specifying using lo/hi (already added to TODO)
- Currently implementing the 6 dunder rich comparison methods for bounds.
- lt/gt/le/ge faces a problem in that InclusiveBound and ExclusiveBound do not know if they are an upper or lower bound
- 2 options:

1. Bounds use a flag to tell if it is upper or lower
- When input to the __init__ in Interval, __init__ will set a flag in each Bound to mark it as higher or lower
- In the comparison operators, check the flag of the self and other and return the result accordingly.

2. Return 2 values
- For every comparison, return 2 values in a list or wtv
- One for if comparing lower bounds and the other for if comparing upper bounds

- I think option 1 is better lol
- Also implement inverting methods for bounds eg changing from InclusiveBound to ExclusiveBound and vice versa
"""

class BaseInterval:
    pass


def typecheck(func):
    def comparison(other):
        if not isinstance(other, BaseBound):
            raise TypeError('Can only compare with other intervals')
        return func(other)
    return comparison


class BaseBound:
    @typecheck
    def __ne__(self, other):
        return not (self == other)


class InclusiveBound(BaseBound):
    def __init__(self, value, ul):
        self.value = Num(value) if Num.isnum(value) else value

    @typecheck
    def __eq__(self, other):
        return isinstance(other, InclusiveBound) and self.value == other.value

    @typecheck
    def __lt__(self, other):
        if self.value < other.value:
            return True
        if self.value > other.value:
            return False
        # self.value == other.value
        if isinstance(other, InclusiveBound):
            return False
        # TODO not done!




class ExclusiveBound(BaseBound):
    def __init__(self, value):
        self.value = Num(value) if Num.isnum(value) else value

    def __eq__(self, other):
        return isinstance(other, ExclusiveBound) and self.value == other.value


class Interval(BaseInterval):
    def __init__(self, lower=ninf, upper=inf, lo=False, hi=False): # TODO accept Bounds as arguments instead of specifying the type of bound manually
        if lower > upper:
            raise ValueError('Lower bound cannot be greater than upper bound')
        if isinstance(lower, BaseBound):
            self.lower = lower
        else:
            if lower == ninf:
                self.lower = ExclusiveBound(lower)
            else:
                self.lower = InclusiveBound(lower) if lo else ExclusiveBound(lower)
        if isinstance(upper, BaseBound):
            self.upper = upper
        else:
            if upper == inf:
                self.upper = ExclusiveBound(upper)
            else:
                self.upper = InclusiveBound(upper) if hi else ExclusiveBound(upper)

    def __invert__(self):
        if self.lower.value == ninf and self.upper.value != inf:
            if isinstance(self.upper, InclusiveBound):
                return Interval(lower=self.upper.value)
            return Interval(lower=self.upper.value, lo=True)
        if self.lower.value != ninf and self.upper.value == inf:
            if isinstance(self.lower, InclusiveBound):
                return Interval(upper=self.lower.value)
            return Interval(upper=self.lower.value, hi=True)
        if self.lower.value == ninf and self.upper.value == inf:
            return None # Empty set

        hi = not isinstance(self.lower, InclusiveBound)
        lo = not isinstance(self.upper, InclusiveBound)
        return Interval(upper=self.lower.value, hi=hi) | Interval(lower=self.upper.value, lo=lo)

    def __and__(self, other):
        if other.lower.value < self.lower.value:
            return other & self

        if other.upper.value < self.upper.value:
            return other
        if other.upper.value > self.upper.value:
            return Interval(other.lower, self.upper)

    def __or__(self, other):
        pass

    def __str__(self):
        if isinstance(self.lower, InclusiveBound):
            s = '['
        else:
            s = '('
        s += f'{self.lower.value}, {self.upper.value}'
        if isinstance(self.upper, InclusiveBound):
            s += ']'
        else:
            s += ')'
        return s


class MultiInterval(BaseInterval):
    def __init__(self):
        pass

    # TODO all set methods

    def __invert__(self):
        pass

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass


if __name__ == '__main__':
    print(Interval())