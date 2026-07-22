from decimal import Decimal
from collections import Counter
from functools import cached_property

from utils import pfactor

__all__ = ['Num', 'Var', 'Sum', 'Prod', 'Frac', 'Exp', 'Eqn',
           'neg_one', 'zero', 'one', 'inf', 'ninf',
           'CORE_TYPES']

# READ BEFORE ADDING!!
# Every core class has to implement the following methods:
# __hash__, decomp, simplify, substitute, get_vars, copy


# TODO implement functions especially log/ln


class _CoreTemplate:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    def __add__(self, other):
        if isinstance(other, _CoreSumTemplate):
            return Sum([self] + other.terms)
        return Sum([self, other])

    def __radd__(self, other):
        if isinstance(other, _CoreSumTemplate):
            return Sum(other.terms + [self])
        return Sum([other, self])

    def __sub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum([self] + (-other).terms)
        return Sum([self, -other])

    def __rsub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum([-other).terms + [self])
        return Sum([other, -self])

    def __mul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            return Prod([self] + other.factors)
        return Prod([self, other])

    def __rmul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            return Prod(other.factors + [self])
        return Prod([other, self])

    def __truediv__(self, other):
        return Frac(self, other)

    def __rtruediv__(self, other):
        return Frac(other, self)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return Exp(self, power)

    def __rpow__(self, other):
        return Exp(other, self)

    def __neg__(self):
        return self * neg_one

    def __pos__(self):
        return self

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        return Counter({self: 1})

    def simplify(self):
        """Simplifies the expression"""
        return self

    def substitute(self, var_map):
        return self

    def copy(self):
        return self


def _num_check(func):
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        if Num.isnum(f):
            return Num(f)
        return f
    return wrapper


class _NumTemplate(Decimal):
    __add__ = _num_check(Decimal.__add__)
    __radd__ = _num_check(Decimal.__radd__)
    __sub__ = _num_check(Decimal.__sub__)
    __rsub__ = _num_check(Decimal.__rsub__)
    __mul__ = _num_check(Decimal.__mul__)
    __rmul__ = _num_check(Decimal.__rmul__)
    __truediv__ = _num_check(Decimal.__truediv__)
    __rtruediv__ = _num_check(Decimal.__rtruediv__)
    __mod__ = _num_check(Decimal.__mod__)
    __rmod__ = _num_check(Decimal.__rmod__)
    __pow__ = _num_check(Decimal.__pow__)
    __rpow__ = _num_check(Decimal.__rpow__)
    __neg__ = _num_check(Decimal.__neg__)
    __pos__ = _num_check(Decimal.__pos__)


class _CoreVarTemplate(_CoreTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"Var('{self.sym}')"

    def __hash__(self):
        return hash(('CoreVar', self.sym))


class _CoreSumTemplate(_CoreTemplate):
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
        if isinstance(other, _CoreSumTemplate):
            return Sum(self.terms + other.terms)
        return Sum(self.terms + [other])

    def __radd__(self, other):
        if isinstance(other, _CoreSumTemplate):
            return Sum(other.terms + self.terms)
        return Sum([other] + self.terms)

    def __iadd__(self, other):
        if isinstance(other, _CoreSumTemplate):
            self.terms.extend(other.terms)
        self.terms.append(other)
        return self

    def __sub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum(self.terms + (-other).terms)
        return Sum(self.terms + [-other])

    def __rsub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum(other.terms + (-self).terms)
        return Sum([other] + (-self).terms)

    def __isub__(self, other):
        self.terms.append(-other)
        return self


class _CoreProdTemplate(_CoreTemplate):
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
        if isinstance(other, _CoreProdTemplate):
            return Prod(self.factors + other.factors)
        return Prod(self.factors + [other])

    def __rmul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            return Prod(other.factors + self.factors)
        return Prod([other] + self.factors)

    def __imul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            self.factors.extend(other.factors)
        self.factors.append(other)
        return self


class _CoreFracTemplate(_CoreTemplate):
    def __str__(self):
        return f'({str(self.numer)} / {str(self.denom)})'

    def __repr__(self):
        return f'Frac({repr(self.numer)}, {repr(self.denom)})'

    def __hash__(self):
        return hash(('CoreFrac', self.numer, self.denom))


class _CoreExpTemplate(_CoreTemplate):
    def __str__(self):
        return f'({str(self.base)} ^ {str(self.power)})'

    def __repr__(self):
        return f'Exp({repr(self.base)}, {repr(self.power)})'

    def __hash__(self):
        return hash(('CoreExp', self.base, self.power))


class _CoreEqnTemplate:
    def __eq__(self, other):
        if not isinstance(other, _CoreEqnTemplate):
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


class Num(_NumTemplate):
    def __init__(self, value, *args, **kwargs):
        Decimal.__init__(str(value), *args, **kwargs)

    def decomp(self):
        if self.to_integral_value() == self:
            return Counter([Num(n) for n in pfactor(self)])
        return Counter({self: 1})

    def simplify(self):
        return self

    def substitute(self, var_map):
        return self

    @cached_property
    def get_vars(self):
        return set()

    def copy(self):
        return self

    @classmethod
    def isnum(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"Num({str(self)})"

    def __hash__(self):
        return hash(('CoreNum', super().__hash__()))


class Var(_CoreVarTemplate):
    def __init__(self, symbol):
        self.sym = symbol

    def substitute(self, var_map):
        if self in var_map:
            return var_map[self]
        return self

    @cached_property
    def get_vars(self):
        return {self}

    def copy(self):
        return Var(self.sym)


neg_one = Num(-1)
zero = Num(0)
one = Num(1)
inf = Num('inf')
ninf = -Num('inf')


class Sum(_CoreSumTemplate):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if Num.isnum(term):
                self.terms.append(Num(term))
            elif isinstance(term, Sum):
                self.terms.extend(term.terms)
            elif term is None or term == []:
                continue
            else:
                self.terms.append(term)
        # Empty case
        if not self.terms:
            self.terms = [zero]

    def simplify(self):
        """Simplifies the expression"""
        decomps = [term.simplify().decomp() for term in self.terms]
        terms_counter = Counter()
        for decomp in decomps:
            coeff = one
            factors = []
            for base, power in tuple(decomp.items()):
                if isinstance(base, Num) and power > 0 and power == int(power):
                    # Force symbolic Exps such as square roots to not get evaluated
                    coeff *= base ** power
                    decomp.pop(base)
                else:
                    factors.append(Exp(base, power))
            terms_counter.update({Prod(factors).simplify(): coeff})
        terms = []
        for term, coeff in terms_counter.items():
            if coeff == zero:
                pass
            elif coeff == one:
                terms.append(term)
            else:
                terms.append(coeff * term)
        if len(terms) == 0:
            return zero
        if len(terms) == 1:
            return terms[0]
        return Sum(terms)

    def substitute(self, var_map):
        return Sum([term.substitute(var_map) for term in self.terms])

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])

    def copy(self):
        return Sum([term.copy() for term in self.terms])


class Prod(_CoreProdTemplate):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if Num.isnum(factor):
                self.factors.append(Num(factor))
            elif isinstance(factor, Prod):
                self.factors.extend(factor.factors)
            elif factor is None or factor == []:
                continue
            else:
                self.factors.append(factor)
        # Empty case
        if not self.factors:
            self.factors = [one]

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        c = Counter()
        for factor in self.factors:
            c.update(factor.decomp())
        return c

    def simplify(self):
        """Simplifies the expression; if factors contain zero, returns zero"""
        decomp = Prod([factor.simplify() for factor in self.factors]).decomp()
        const = one
        factors = []
        for base, power in decomp.items():
            expr = Exp(base, power).simplify()
            if isinstance(expr, Num):
                const *= expr
            else:
                factors.append(expr)
        if const == zero:
            return zero
        if len(factors) == 0:
            return const
        if const == one and len(factors) == 1:
            return factors[0]
        if const == one and len(factors) > 1:
            return Prod(factors)
        return const * Prod(factors)

    def substitute(self, var_map):
        return Prod([term.substitute(var_map) for term in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])

    def copy(self):
        return Prod([factor.copy() for factor in self.factors])


class Frac(_CoreFracTemplate):
    def __init__(self, numer, denom):
        self.numer = Num(numer) if Num.isnum(numer) else numer
        self.denom = Num(denom) if Num.isnum(denom) else denom

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        numers = self.numer.decomp()
        denoms = self.denom.decomp()
        numers.subtract(denoms)
        return numers

    def simplify(self):
        """Returns the fraction with simplified numerator and denominator"""
        numer = self.numer.simplify()
        denom = self.denom.simplify()
        if numer == zero and denom != zero:
            return zero
        if denom == one:
            return numer
        if numer == zero and denom == zero:
            return Frac(zero, zero)
        if isinstance(numer, Num) and isinstance(denom, Num):
            if numer % denom == 0:
                return numer / denom
        return Frac(numer, denom)

    def substitute(self, var_map):
        return Frac(self.numer.substitute(var_map), self.denom.substitute(var_map))

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    def copy(self):
        return Frac(self.numer.copy(), self.denom.copy())


class Exp(_CoreExpTemplate):
    def __init__(self, base, power):
        self.base = Num(base) if Num.isnum(base) else base
        self.power = Num(power) if Num.isnum(power) else power

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        if isinstance(self.power, Num):
            return Counter({self.base: self.power})
        return Counter({self: 1})

    def simplify(self):
        """Simplifies the expression"""
        base = self.base.simplify()
        power = self.power.simplify()
        if power == one:
            return base
        if base == one or (power == zero and base != zero):
            return one
        if base == zero and power != zero:
            return zero
        if base == zero and power == zero:
            return Exp(zero, zero)
        if isinstance(base, Num) and isinstance(power, Num):
            if base == int(base) and power == int(power):
                return base ** power
        return Exp(base, power)

    def substitute(self, var_map):
        return self.base.substitute(var_map) ** self.power.substitute(var_map)

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    def copy(self):
        return Exp(self.base.copy(), self.power.copy())


class Eqn(_CoreEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = Num(lhs) if Num.isnum(lhs) else lhs
        self.rhs = Num(rhs) if Num.isnum(rhs) else rhs

    def simplify(self):
        return Eqn(self.lhs.simplify(), self.rhs.simplify())

    def swap(self):
        return Eqn(self.rhs, self.lhs)

    def substitute(self):
        pass

    @cached_property
    def get_vars(self):
        return self.lhs.get_vars | self.rhs.get_vars

    def copy(self):
        return Eqn(self.lhs.copy, self.rhs.copy)


class Func: # TODO this has been on todo for the longest time
    def __init__(self):
        pass


CORE_TYPES = (Num, Var, Sum, Prod, Frac, Exp, Eqn)


if __name__ == '__main__':
    x = Var('x')
    y = Var('y')

    # expr = ( (3*x**2*y**3 - 2*x*y**2 + 4*x**3*y) + (2*x**2*y**3 + 5*x*y**2 - x**3*y) + (4*x**2*y**3 + 3*x*y**2 - 5*x**3*y) ) + ( (x**2*y**3 + 4*x*y**2 - 2*x**3*y) + (2*x**2*y**3 - x*y**2 + 3*x**3*y) + (3*x**2*y**3 - 2*x*y**2 + x**3*y) )
    # print(expr.simplify()) # ((15 * (x ^ 2) * (y ^ 3)) + (7 * x * (y ^ 2)))

    expr = Prod((Exp(3, 0.5), Exp(2, 0.5)))
    print(expr.simplify())