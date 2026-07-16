from collections import defaultdict, Counter
from itertools import product
from functools import cached_property
from decimal import Decimal

from utils import pfactor

__all__ = ['Num', 'Var', 'Sum', 'Prod', 'Frac', 'Exp', 'Eqn',
           'neg_one', 'zero', 'one', 'inf', 'ninf',
           'CORE_TYPES']

# READ BEFORE ADDING!!
# Every core class has to implement the following methods:
# __hash__, decomp, group, simplify, expand, factorise, substitute, get_vars, copy


# TODO check sub and rsub for CoreTemplate and SumTemplate
# TODO implement functions especially log/ln
# TODO force frac and exp of Nums to remain symbolic instead of getting evaluated
# TODO change group and simplify to use collections.counter


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

    def group(self):
        """Collects like terms"""
        return self

    def simplify(self):
        """Simplifies the expression"""
        return self

    def expand(self):
        return self

    def factorise(self, out=None):
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
        return hash(('CoreEqn', self.lhs, self.rhs))


class Num(_NumTemplate):
    def __init__(self, value, *args, **kwargs):
        Decimal.__init__(str(value), *args, **kwargs)

    def decomp(self):
        if self.to_integral_value() == self:
            return Counter([Num(n) for n in pfactor(self)])
        return Counter({self: 1})

    def group(self):
        return self

    def simplify(self):
        return self

    def expand(self):
        return self

    def factorise(self, out=None):
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

    def group(self):
        """Collects like terms"""
        decomp = [list(term.group().decomp().elements()) for term in self.terms]
        unique = defaultdict(int)
        for term in decomp:
            # Multiplying constants in each term to get coefficient
            coeff = one
            for i, factor in reversed(list(enumerate(term))):
                if Num.isnum(factor):
                    coeff *= term.pop(i)
            # Accumulating coefficients of like terms
            term = Prod(term) # term was a list
            unique[term] += coeff
        output = [coeff * term for term, coeff in unique.items()]
        return Sum(output)

    def simplify(self):
        """Simplifies the expression"""
        terms = self.group().terms
        terms = [term.simplify() for term in terms]
        terms = [term for term in terms if term != zero]
        if len(terms) == 0:
            return zero
        if len(terms) == 1:
            return terms[0]
        return Sum(terms)

    def expand(self):
        """Returns the expanded form of each term"""
        return Sum([term.expand() for term in self.terms])

    def factorise(self, out=None):
        """Factorises the Sum; if out is provided, factorises it out"""
        if out is not None:
            return self._factorise_out(out)
        decomp = [term.decomp() for term in self.terms]
        gcd = one
        decomp0 = decomp[0].copy()
        # TODO use collections.Counter to optimise
        for factor in decomp0:
            if all([factor in factors for factors in decomp]):
                for factors in decomp:
                    factors.remove(factor)
                gcd *= factor
        factorised = [Prod(term) for term in decomp]
        return gcd * Sum(factorised)

    def _factorise_out(self, out):
        """Factorise helper method"""
        factorised = [term / out for term in self.terms]
        return out * Sum(factorised)

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
        # decomp = [] # TODO use itertools.chain
        # for factor in self.factors:
        #     decomp.extend(factor.decomp())
        # return decomp
        c = Counter()
        for factor in self.factors:
            c.update(factor.decomp())
        return c

    def group(self):
        """Collects like factors into exponents"""
        unique = defaultdict(int)
        const = 1
        for factor in self.factors:
            # Multiplying to get constant
            if isinstance(factor, Num):
                const *= factor
                continue
            # Accumulating powers of like factors
            if isinstance(factor, Exp):
                base, power = factor.base, factor.power
            else:
                base, power = factor, 1
            unique[base] += power
        output = [base ** power for base, power in unique.items()]
        return const * Prod(output)

    def simplify(self):
        """Simplifies the expression; if factors contain zero, returns zero"""
        factors = self.group().factors
        factors = [factor.simplify() for factor in factors]
        if zero in factors:
            return zero
        factors = [factor for factor in factors if factor != one]
        if len(factors) == 0:
            return one
        if len(factors) == 1:
            return factors[0]
        return Prod(factors)

    def expand(self):
        """Returns an expansion of the product following distributive law"""
        # First expand all factors to get rid of Exp
        prod = [factor.expand() for factor in self.factors]
        # Get all factors as a list of their terms
        factors = []
        for factor in prod:
            if isinstance(factor, Sum):
                factors.append(factor.terms)
            else:
                factors.append([factor])
        # Get all combinations of terms from each factor using itertools product
        new_terms = product(*factors)
        output = [Prod(list(term)) for term in new_terms]
        return Sum(output)

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
        # denoms = [denom ** neg_one for denom in denoms]
        # return numers + denoms
        numers.subtract(denoms)
        return numers

    def simplify(self):
        """Returns the fraction with simplified numerator and denominator"""
        return self.numer.simplify() / self.denom.simplify()

    def expand(self):
        """Returns an expansion of the numerator and denominator"""
        return Frac(self.numer.expand(), self.denom.expand())

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

    def decomp(self): # TODO make it return only numeric and fractional part
        """Decomposes the expression into its constituent factors"""
        # i, f = divmod(self.power, one)
        # if i > zero:
        #     output = [self.base for _ in range(int(i))]
        # else:
        #     output = [self.base ** neg_one for _ in range(-int(i))]
        # if f != zero:
        #     output.append(self.base ** f)
        # return output
        if isinstance(self.power, Num):
            return Counter({self.base: self.power})
        return super().decomp()

    def simplify(self):
        """Simplifies the expression"""
        return self.base.simplify() ** self.power.simplify()

    def expand(self):
        """Returns an expansion of the exponential"""
        decomp = self.decomp()
        if len(decomp) == 1:
            return decomp[0]
        return Prod(decomp).expand()

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
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        return Eqn(lhs, rhs)

    # def isequal(self):
    #     return self.lhs == self.rhs

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


CORE_TYPES = (Num, Var, Sum, Prod, Frac, Exp)


if __name__ == '__main__':
    x = Var('x')
    # expr = (x+1)**2 * (x+1)**3
    # expr = expr.expand().simplify()
    expr = neg_one * 17/x**2 * x
    print(expr)
    expr = expr.expand().simplify()
    print(expr)