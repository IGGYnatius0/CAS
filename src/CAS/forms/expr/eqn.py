from functools import cached_property

from .registry import FORMS
from .utils import make_form
from CAS.core.expr import Eqn


class FormEqn:
    def __init__(self, lhs, rhs):
        self.lhs = make_form(lhs)
        self.rhs = make_form(rhs)

    def match(self, expr, var_map):
        if not isinstance(expr, Eqn):
            return False
        matches = FORMS.MultiConstraint(2)
        matches[0, 0] = self.lhs.match(expr.lhs, var_map.copy())
        matches[0, 1] = self.lhs.match(expr.rhs, var_map.copy())
        matches[1, 0] = self.rhs.match(expr.lhs, var_map.copy())
        matches[1, 1] = self.rhs.match(expr.rhs, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        if not self.lhs.isconst:
            return False
        if not self.rhs.isconst:
            return False
        return True

    def group_consts(self):
        return FormEqn(self.lhs.group_consts(), self.rhs.group_consts())

    @cached_property
    def get_consts(self):
        return self.lhs.get_consts | self.rhs.get_consts

    @cached_property
    def get_vars(self):
        return self.lhs.get_vars | self.rhs.get_vars

    def substitute_consts(self, const_map):
        return FormEqn(self.lhs.substitute_consts(const_map), self.rhs.substitute_consts(const_map))

    def to_coretype(self, const_map, var_map={}):
        return Eqn(self.lhs.to_coretype(const_map, var_map),
                   self.rhs.to_coretype(const_map, var_map))


    def __str__(self):
        return f'{str(self.lhs)} = {str(self.rhs)}'

    def __repr__(self):
        return f'{repr(self.lhs)} = {repr(self.rhs)}'

    def __hash__(self):
        return hash(('FORMS.eqn', self.lhs, self.rhs))

    def __add__(self, other):
        return FORMS.eqn(self.lhs + other.lhs, self.rhs + other.rhs)

    def __radd__(self, other):
        return FORMS.eqn(other.lhs + self.lhs,
                       other.rhs + self.rhs)

    def __iadd__(self, other):
        self.lhs += other.lhs
        self.rhs += other.rhs
        return self

    def __sub__(self, other):
        return FORMS.eqn(self.lhs - other.lhs, self.rhs - other.rhs)

    def __rsub__(self, other):
        return FORMS.eqn(other.lhs - self.lhs, other.rhs - self.rhs)

    def __isub__(self, other):
        self.lhs -= other.lhs
        self.rhs -= other.rhs
        return self

    def __mul__(self, other):
        return FORMS.eqn(self.lhs * other.lhs, self.rhs * other.rhs)

    def __rmul__(self, other):
        return FORMS.eqn(other.lhs * self.lhs, other.rhs * self.rhs)

    def __imul__(self, other):
        self.lhs *= other.lhs
        self.rhs *= other.rhs
        return self

    def __truediv__(self, other):
        return FORMS.eqn(self.lhs / other.lhs, self.rhs / other.rhs)

    def __rtruediv__(self, other):
        return FORMS.eqn(other.lhs / self.lhs, other.rhs / self.rhs)

    def __itruediv__(self, other):
        self.lhs /= other.lhs
        self.rhs /= other.rhs
        return self

    def __pow__(self, other):
        return FORMS.eqn(self.lhs ** other.lhs, self.rhs ** other.rhs)

    def __rpow__(self, other):
        return FORMS.eqn(other.lhs ** self.lhs, other.rhs ** self.rhs)

    def __ipow__(self, other):
        self.lhs **= other.lhs
        self.rhs **= other.rhs
        return self


FORMS.eqn = FormEqn