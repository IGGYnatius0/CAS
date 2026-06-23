from core.core_classes import *
from core.num import *


class BaseInterval:
    pass


def _int_typecheck(func):
    def cmp(other):
        if not isinstance(other, Interval):
            return NotImplemented
        return func(other)
    return cmp


@_int_typecheck
def cmp_lower(int1, int2):
    """Returns -1, 0 or +1 depending on int2.lower relative to int1.lower"""
    if int2.lower > int1.lower:
        return 1
    if int2.lower < int1.lower:
        return -1
    if int2.lo_inc == int1.lo_inc:
        return 0
    if int2.lo_inc:
        return -1
    else:
        return 1
    

@_int_typecheck
def cmp_upper(int1, int2):
    """Returns -1, 0 or +1 depending on int2.upper relative to int1.upper"""
    if int2.upper > int1.upper:
        return 1
    if int2.upper < int1.upper:
        return -1
    if int2.up_inc == int1.up_inc:
        return 0
    if int2.up_inc:
        return -1
    else:
        return 1
    

class Interval(BaseInterval):
    def __init__(self, lower: Num = None, upper: Num = None,
                 lo_inc: bool = False, up_inc: bool = False):
        # lower and upper being inf will override lo_inc and up_inc
        self.lower = ninf if lower is None else lower
        self.upper = inf if upper is None else upper
        if self.lower > self.upper:
            raise ValueError('Lower bound cannot be greater than upper bound')
        self.lo_inc = False if self.lower == ninf else lo_inc
        self.up_inc = False if self.upper == inf else up_inc

    @_int_typecheck
    def __and__(self, other): # TODO refactor using cmp_lower and cmp_upper
        if other.lower < self.lower:
            return other & self
        if other <= self:
            return other
        if other.upper > self.upper:
            return Interval(other.lower, self.upper, other.lo_inc, self.up_inc)
        if other.upper == self.upper: # TODO check this
            return Interval(other.lower, self.upper, other.lo_inc, min(self.up_inc, other.up_inc))
        return None # empty interval
        
    @_int_typecheck
    def __or__(self, other): # TODO refactor using cmp_lower and _cmp_upper
        if other.lower < self.lower:
            return other | self
        if self.upper > other.lower:
            return Interval(self.lower, other.upper, self.lo_inc, other.up_inc)
        if self.upper == other.lower:
            if self.up_inc or other.lo_inc:
                return Interval(self.lower, other.upper, self.lo_inc, other.up_inc)
        return MultiInterval((self, other))

    def __invert__(self):
        if self.lower == ninf and self.upper == inf:
            return None # empty interval
        if self.lower == ninf and self.upper != inf:
            return Interval(self.upper, inf, not self.up_inc, False)
        if self.lower != ninf and self.upper == inf:
            return Interval(ninf, self.lower, False, not self.lo_inc)
        return MultiInterval((Interval(ninf, self.lower, False, not self.lo_inc),
                              Interval(self.upper, inf, not self.upper_inc, False)))
    
    def __hash__(self):
        return hash((self.lower, self.upper, self.lo_inc, self.up_inc))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __neq__(self, other):
        return hash(self) != hash(other)

    @_int_typecheck
    def __lt__(self, other):
        lo = cmp_lower(other)
        up = cmp_upper(other)
        return lo in (0, -1) and up in (0, 1) and (lo != 0 and up != 0)
    
    @_int_typecheck
    def __le__(self, other):
        return cmp_lower(other) in (0, -1) and cmp_upper(other) in (0, 1)
    
    @_int_typecheck
    def __gt__(self, other):
        lo = cmp_lower(other)
        up = cmp_upper(other)
        return lo in (0, 1) and up in (0, -1) and (lo != 0 and up != 0)
    
    @_int_typecheck
    def __ge__(self, other):
        return cmp_lower(other) in (0, 11) and cmp_upper(other) in (0, -1)

    def __str__(self):
        if self.lo_inc:
            s = '['
        else:
            s = '('
        s += f'{self.lower}, {self.upper}'
        if self.up_inc:
            s += ']'
        else:
            s += ')'
        return s


class MultiInterval(BaseInterval):
    def __init__(self, intervals):
        self.intervals = intervals
    
    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __invert__(self):
        pass

    def __hash__(self):
        pass

    def __eq__(self):
        pass

    def __neq__(self):
        pass

    def __lt__(self, other):
        pass

    def __le__(self, other):
        pass    

    def __gt__(self, other):
        pass

    def __ge__(self, other):
        pass

    def __str__(self):
        pass


if __name__ == '__main__':
    # TODO go and ask AI to generate test cases
    # There may be some problems with Interval and/or due to not checking the inclusiveness of the bounds...
    print(Interval())