from functools import cached_property

from .registry import EXPRS
from .utils import make_expr
from CAS.exceptions import InvalidSubroutineError


class Eqn:
    def __init__(self, lhs, rhs):
        self.lhs = make_expr(lhs)
        self.rhs = make_expr(rhs)

    def swap(self):
        return Eqn(self.rhs, self.lhs)

    @cached_property
    def isnum(self):
        raise InvalidSubroutineError("Cannot use .isnum method on Eqn")

    @cached_property
    def get_vars(self):
        return self.lhs.get_vars | self.rhs.get_vars

    def copy(self):
        return Eqn(self.lhs.copy, self.rhs.copy)

    def apply(self, func, *args, to_list=False):
        eqn = Eqn(func(self.lhs, *args), func(self.rhs, *args))
        if to_list:
            return eqn.lhs, eqn.rhs
        return eqn


    def __eq__(self, other):
        if not isinstance(other, Eqn):
            return False
        return ((self.lhs == other.lhs and self.rhs == other.rhs) or
                (self.lhs == other.rhs and self.rhs == other.lhs))

    def __add__(self, other):
        return Eqn(self.lhs + other.lhs, self.rhs + other.rhs)

    def __radd__(self, other):
        return Eqn(other.lhs + self.lhs, other.rhs + self.rhs)

    def __iadd__(self, other):
        self.rhs += other.rhs
        self.lhs += other.lhs
        return self

    def __sub__(self, other):
        return Eqn(self.lhs - other.lhs, self.rhs - other.rhs)

    def __rsub__(self, other):
        return Eqn(other.lhs - self.lhs, other.rhs - self.rhs)

    def __isub__(self, other):
        self.rhs -= other.rhs
        self.lhs -= other.lhs
        return self

    def __mul__(self, other):
        return Eqn(self.lhs * other.lhs, self.rhs * other.rhs)

    def __rmul__(self, other):
        return Eqn(other.lhs * self.lhs, other.rhs * self.rhs)

    def __imul__(self, other):
        self.rhs *= other.rhs
        self.lhs *= other.lhs
        return self

    def __truediv__(self, other):
        return Eqn(self.lhs / other.lhs, self.rhs / other.rhs)

    def __rtruediv__(self, other):
        return Eqn(other.lhs / self.lhs, other.rhs / self.rhs)

    def __itruediv__(self, other):
        self.rhs /= other.rhs
        self.lhs /= other.lhs
        return self

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return Eqn(self.lhs ** power.lhs, self.rhs ** power.rhs)

    def __rpow__(self, other):
        return Eqn(other.lhs ** self.lhs, other.rhs ** self.rhs)

    def __ipow__(self, other):
        self.rhs **= other.rhs
        self.lhs **= other.lhs
        return self

    def __str__(self):
        return f'{str(self.lhs)} = {str(self.rhs)}'

    def __repr__(self):
        return f'Eqn({repr(self.lhs)}, {repr(self.rhs)})'

    def __hash__(self):
        hashes = (hash(self.lhs), hash(self.rhs))
        return hash(('CoreEqn', min(hashes), max(hashes)))


EXPRS.eqn = Eqn