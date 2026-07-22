from itertools import pairwise
from core.classes import *


__all__ = ['Interval', 'MultiInterval', 'REALS', 'from_str']


class BaseInterval:
    pass


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
    

def cmp_upper(int1, int2):
    """Returns -1, 0 or +1 depending on int2.upper relative to int1.upper"""
    if int2.upper > int1.upper:
        return 1
    if int2.upper < int1.upper:
        return -1
    if int2.up_inc == int1.up_inc:
        return 0
    if int2.up_inc:
        return 1
    else:
        return -1
    

def from_str(s):
    if s[0] not in '([':
        raise ValueError("Invalid interval string")
    if s[-1] not in ')]':
        raise ValueError("Invalid interval string")
    if ',' not in s or s.count(',') != 1:
        raise ValueError("Invalid interval string")
    bounds = s[1:-1].split(',')
    lower = Num(bounds[0].strip())
    upper = Num(bounds[1].strip())
    lo_inc = s[0] == '['
    up_inc = s[-1] == ']'
    return Interval(lower, upper, lo_inc, up_inc)


def _interval_typecheck(func):
    def cmp(self, other):
        if isinstance(other, Num):
            other = Interval(other, other, True, True)
        if not isinstance(other, Interval):
            return NotImplemented
        return func(self, other)
    return cmp


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

    @_interval_typecheck
    def __and__(self, other):
        if cmp_lower(self, other) == -1:
            return other & self
        if cmp_upper(self, other) != 1:
            return other
        if other.lower < self.upper or \
            (other.lower == self.upper and other.lo_inc == self.up_inc == True):
            return Interval(other.lower, self.upper, other.lo_inc, self.up_inc)
        return None # empty interval
        
    @_interval_typecheck
    def __or__(self, other):
        if cmp_lower(self, other) == -1:
            return other | self
        if cmp_upper(self, other) != 1:
            return self
        if other.lower < self.upper or \
            (other.lower == self.upper and \
             not (other.lo_inc == self.up_inc == False)):
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
                              Interval(self.upper, inf, not self.up_inc, False)))
    
    def __hash__(self):
        return hash((hash((self.lower, self.upper, self.lo_inc, self.up_inc)),))

    @_interval_typecheck
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @_interval_typecheck
    def __contains__(self, other):
        return other <= self

    @_interval_typecheck
    def __lt__(self, other):
        lo = cmp_lower(self, other)
        up = cmp_upper(self, other)
        return lo in (0, -1) and up in (0, 1) and (lo != 0 and up != 0)
    
    @_interval_typecheck
    def __le__(self, other):
        return cmp_lower(self, other) in (0, -1) and cmp_upper(self, other) in (0, 1)
    
    @_interval_typecheck
    def __gt__(self, other):
        lo = cmp_lower(self, other)
        up = cmp_upper(self, other)
        return lo in (0, 1) and up in (0, -1) and (lo != 0 and up != 0)
    
    @_interval_typecheck
    def __ge__(self, other):
        return cmp_lower(self, other) in (0, 1) and cmp_upper(self, other) in (0, -1)

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


def _multiinterval_typecheck(func):
    def cmp(self, other):
        if isinstance(other, Num):
            other = Interval(other, other, True, True)
        if not isinstance(other, (Interval, MultiInterval)):
            return NotImplemented
        return func(self, other)
    return cmp


class MultiInterval(BaseInterval):
    def __init__(self, intervals):
        for lower, upper in pairwise(intervals):
            if lower.upper > upper.lower:
                raise ValueError('Intervals must be in order and must not overlap')
        self.intervals = tuple(intervals)

    @_multiinterval_typecheck
    def __and__(self, other):
        if isinstance(other, Interval):
            other = MultiInterval((other,))
        if not isinstance(other, MultiInterval):
            return NotImplemented
        
        # Interval intersection algorithm
        A, B = self.intervals, other.intervals
        result = []
        i = j = 0
        while i < len(A) and j < len(B):
            overlap = A[i] & B[j]
            if overlap is not None:
                result.append(overlap)
            cmp = cmp_upper(A[i], B[j])
            if cmp == 1:
                i += 1
            elif cmp == -1:
                j += 1
            else:
                i += 1
                j += 1
        
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        return MultiInterval(result)

    @_multiinterval_typecheck
    def __rand__(self, other):
        return self.__and__(other)

    @_multiinterval_typecheck
    def __or__(self, other):
        if isinstance(other, Interval):
            other = MultiInterval((other,))
        if not isinstance(other, MultiInterval):
            return NotImplemented
        A, B = list(self.intervals), list(other.intervals)

        # Merging intervals based on lower bound like mergesort
        merged = []
        while A and B:
            if cmp_lower(A[0], B[0]) != 1: # A[0] >= B[0]
                merged.append(A.pop(0))
            else:
                merged.append(B.pop(0))
        merged.extend(A)
        merged.extend(B)

        # Combining intervals
        last = merged[0]
        result = []
        for interval in merged[1:]:
            last |= interval
            if isinstance(last, MultiInterval):
                result.append(last.intervals[0])
                last = last.intervals[1]
        result.append(last)
        
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        return MultiInterval(result)

    @_multiinterval_typecheck
    def __ror__(self, other):
        return self.__or__(other)

    def __invert__(self):
        # TODO optimize this by going through self.intervals and directly
        # creating new intervals in between the existing ones instead of
        # and'ing the complement of every interval together
        result = Interval()
        for interval in self.intervals:
            result &= ~interval
        return result

    def __hash__(self):
        return hash(self.intervals)
    
    @_multiinterval_typecheck
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @_multiinterval_typecheck
    def __contains__(self, other):
        return other <= self

    @_multiinterval_typecheck
    def __lt__(self, other):
        return self & other == self and self != other

    @_multiinterval_typecheck
    def __le__(self, other):
        return self & other == self

    @_multiinterval_typecheck
    def __gt__(self, other):
        return self & other == other and self != other

    @_multiinterval_typecheck
    def __ge__(self, other):
        return self & other == other

    def __str__(self):
        out = []
        for i in self.intervals:
            out.append(str(i))
        return ', '.join(out)


REALS = Interval()


if __name__ == '__main__':
    # TODO test cases
    s1 = from_str('(-1, 3)')
    s2 = from_str('[5, 10]')
    s3 = from_str('[2, 7)')
    s4 = (s1 | s2) & s3
    print(s4)
    print(~s4)
    print(Num(1) in s1)