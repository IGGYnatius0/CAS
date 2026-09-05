import math
from decimal import Decimal
from collections import Counter
from functools import cached_property

from .registry import EXPRS


__all__ = ['CoreBaseExpr',
           'CoreBaseNum', 'CoreBaseVar', 'CoreBaseSum', 'CoreBaseProd',
           'CoreBaseFrac', 'CoreBaseExp']


class CoreBaseExpr:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    def __add__(self, other):
        if isinstance(other, EXPRS['sum']):
            return EXPRS['sum']([self] + other.terms)
        return EXPRS['sum']([self, other])

    def __radd__(self, other):
        if isinstance(other, EXPRS['sum']):
            return EXPRS['sum'](other.terms + [self])
        return EXPRS['sum']([other, self])

    def __sub__(self, other):
        return EXPRS['sum']([self, -other])

    def __rsub__(self, other):
        return EXPRS['sum']([other, -self])

    def __mul__(self, other):
        if isinstance(other, EXPRS['prod']):
            return EXPRS['prod']([self] + other.factors)
        return EXPRS['prod']([self, other])

    def __rmul__(self, other):
        if isinstance(other, EXPRS['prod']):
            return EXPRS['prod'](other.factors + [self])
        return EXPRS['prod']([other, self])

    def __truediv__(self, other):
        return EXPRS['frac'](self, other)

    def __rtruediv__(self, other):
        return EXPRS['frac'](other, self)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return EXPRS['exp'](self, power)

    def __rpow__(self, other):
        return EXPRS['exp'](other, self)

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        return Counter({self: 1})

    def expand(self):
        return self

    def factorize(self):
        return self

    def simplify(self):
        """Simplifies the expression"""
        return self

    def substitute_vars(self, var_map):
        return self

    def copy(self):
        return self

    @cached_property
    def get_vars(self):
        return set()

    @cached_property
    def isnum(self):
        return False

    def eval_nums(self):
        return self

    def group_nums(self):
        return self


class CoreBaseNum(CoreBaseExpr, int):
    def __repr__(self):
        return f"Num({str(self)})"

    def __hash__(self):
        # hash('-1') = 357669246384252548
        return super(int).__hash__() if self != -1 else 357669246384252548


class CoreBaseVar(CoreBaseExpr):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"Var('{self.sym}')"

    def __hash__(self):
        return hash(('CoreVar', self.sym))


class CoreBaseSum(CoreBaseExpr):
    def __str__(self):
        terms = [str(term) for term in self.terms]
        return f'({" + ".join(terms)})'

    def __repr__(self):
        terms = [repr(term) for term in self.terms]
        return f'Sum([{", ".join(terms)}])'

    def __hash__(self):
        hashes = [hash(term) for term in self.terms]
        return hash(('CoreSum',) + tuple(sorted(hashes)))

    def __add__(self, other):
        if isinstance(other, EXPRS['sum']):
            return EXPRS['sum'](self.terms + other.terms)
        return EXPRS['sum'](self.terms + [other])

    def __radd__(self, other):
        if isinstance(other, EXPRS['sum']):
            return EXPRS['sum'](other.terms + self.terms)
        return EXPRS['sum']([other] + self.terms)

    def __sub__(self, other):
        return EXPRS['sum'](self.terms + [-other])

    def __rsub__(self, other):
        return EXPRS['sum']([other] + (-self).terms)


class CoreBaseProd(CoreBaseExpr):
    def __str__(self):
        factors = [str(factor) for factor in self.factors]
        return f'({" * ".join(factors)})'

    def __repr__(self):
        factors = [repr(factor) for factor in self.factors]
        return f'Prod([{", ".join(factors)}])'

    def __hash__(self):
        hashes = [hash(factor) for factor in self.factors]
        return hash(('CoreProd',) + tuple(sorted(hashes)))

    def __mul__(self, other):
        if isinstance(other, EXPRS['prod']):
            return EXPRS['prod'](self.factors + other.factors)
        return EXPRS['prod'](self.factors + [other])

    def __rmul__(self, other):
        if isinstance(other, EXPRS['prod']):
            return EXPRS['prod'](other.factors + self.factors)
        return EXPRS['prod']([other] + self.factors)


class CoreBaseFrac(CoreBaseExpr):
    def __str__(self):
        return f'({str(self.numer)} / {str(self.denom)})'

    def __repr__(self):
        return f'Frac({repr(self.numer)}, {repr(self.denom)})'

    def __hash__(self):
        return hash(('CoreFrac', self.numer, self.denom))


class CoreBaseExp(CoreBaseExpr):
    def __str__(self):
        return f'({str(self.base)} ^ {str(self.power)})'

    def __repr__(self):
        return f'Exp({repr(self.base)}, {repr(self.power)})'

    def __hash__(self):
        return hash(('CoreExp', self.base, self.power))