from decimal import Decimal
from collections import Counter, defaultdict
from itertools import product
from functools import cached_property

from core.pfactor import pfactor

__all__ = ['Num', 'Var', 'Sum', 'Prod', 'Frac', 'Exp', 'Eqn',
           'neg_one', 'zero', 'one', 'inf', 'ninf',
           'CORE_TYPES', 'CORE_EXPR',
           'decomp2prod']

# READ BEFORE ADDING!!
# Every core class has to implement the following methods:
# __hash__, decomp, expand, factorize, simplify, substitute_vars, get_vars, copy


# TODO implement functions especially log/ln
# TODO __init__ which pull from classes and intervals


def _operator_typecheck(func):
    def wrapper(self, other):
        if isinstance(other, CORE_EXPR + (int, float, Decimal)):
            return func(self, other)
        return NotImplemented
    return wrapper


class _CoreTemplate:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    @_operator_typecheck
    def __add__(self, other):
        if isinstance(other, _CoreSumTemplate):
            return Sum([self] + other.terms)
        return Sum([self, other])

    @_operator_typecheck
    def __radd__(self, other):
        if isinstance(other, _CoreSumTemplate):
            return Sum(other.terms + [self])
        return Sum([other, self])

    @_operator_typecheck
    def __sub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum([self] + (-other).terms)
        return Sum([self, -other])

    @_operator_typecheck
    def __rsub__(self, other):
        # if isinstance(other, CoreSumTemplate):
        #     return Sum([-other).terms + [self])
        return Sum([other, -self])

    @_operator_typecheck
    def __mul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            return Prod([self] + other.factors)
        return Prod([self, other])

    @_operator_typecheck
    def __rmul__(self, other):
        if isinstance(other, _CoreProdTemplate):
            return Prod(other.factors + [self])
        return Prod([other, self])

    @_operator_typecheck
    def __truediv__(self, other):
        return Frac(self, other)

    @_operator_typecheck
    def __rtruediv__(self, other):
        return Frac(other, self)

    @_operator_typecheck
    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return Exp(self, power)

    @_operator_typecheck
    def __rpow__(self, other):
        return Exp(other, self)

    def __neg__(self):
        return self * neg_one

    def __pos__(self):
        return self

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        return Counter({self: one})

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


def _num_check(func):
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        if Num.is_num(f):
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
    __abs__ = _num_check(Decimal.__abs__)
    def __hash__(self):
        if self == neg_one: # to prevent hash collision between -1 and -2
            return -1279179286899660244 # hash('-1')
        return super().__hash__()


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
        if int(self) == self:
            f = pfactor(self)
            return Counter({Num(base): Num(power) for base, power in f.items()})
        else:
            return Frac(*self.as_integer_ratio()).decomp()

    def expand(self):
        return self

    def factorize(self):
        return self

    def simplify(self):
        return self

    def substitute_vars(self, var_map):
        return self

    @cached_property
    def get_vars(self):
        return set()
    
    @cached_property
    def isnum(self):
        return True

    def copy(self):
        return self
    
    def eval_nums(self):
        return self

    @classmethod
    def is_num(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"Num({str(self)})"

    def __hash__(self):
        return hash(('CoreNum', super().__hash__()))


class Var(_CoreVarTemplate):
    def __init__(self, symbol):
        self.sym = symbol

    def substitute_vars(self, var_map):
        if self in var_map:
            return var_map[self]
        return self

    @cached_property
    def get_vars(self):
        return {self}
    
    @cached_property
    def isnum(self):
        return False

    def copy(self):
        return Var(self.sym)
    
    def eval_nums(self):
        return self


neg_one = Num(-1)
zero = Num(0)
one = Num(1)
inf = Num('inf')
ninf = -Num('inf')


class Sum(_CoreSumTemplate):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if Num.is_num(term):
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

    def expand(self):
        return Sum([term.expand() for term in self.terms])

    def factorize(self):
        decomps = [term.factorize().decomp() for term in self.terms]
        common = decomps[0].copy()
        for decomp in decomps[1:]:
            common &= decomp
        for i in range(len(decomps)):
            decomps[i].subtract(common)

        # Convert from Counter to list of Exp
        common_list = []
        for expr, power in common.items():
            common_list.append(Exp(expr, power))
        common_prod = Prod(common_list)

        terms_list = []
        for decomp in decomps:
            temp = []
            for expr, power in decomp.items():
                if power != zero:
                    temp.append(Exp(expr, power))
            terms_list.append(Prod(temp))
        terms_sum = Sum(terms_list)

        return Prod([common_prod, terms_sum])

    @staticmethod
    def sum_fracs(fracs):
        numer = zero
        denom = one
        for i, (_, d) in enumerate(fracs):
            temp = one
            for j, frac in enumerate(fracs):
                if i == j:
                    temp *= frac[0]
                else:
                    temp *= frac[1]
            numer += temp
            denom *= d
        return Frac(numer, denom).simplify()

    def simplify(self):
        decomps = [term.simplify().decomp() for term in self.terms]
        terms_dict = defaultdict(list)
        for decomp in decomps:
            numer = one
            denom = one
            factors = []
            for base, power in decomp.items():
                if isinstance(base, Num) and isinstance(power, Num) and int(base) == base and int(power) == power:
                    if power < 0:
                        denom *= base ** -power
                    else:
                        numer *= base ** power
                else:
                    factors.append(Exp(base, power))
            terms_dict[Prod(factors).simplify()].append((numer, denom))
        terms = [(factors * self.sum_fracs(fracs)).simplify() for factors, fracs in terms_dict.items()]

        if len(terms) == 0:
            return zero
        if len(terms) == 1:
            return terms[0]
        return Sum(terms)

    def substitute_vars(self, var_map):
        return Sum([term.substitute_vars(var_map) for term in self.terms])

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
        return Sum([term.copy() for term in self.terms])
    
    def eval_nums(self):
        num = zero
        terms = []
        has_num = False
        for term in self.terms:
            if term.isnum:
                num += term.eval_nums()
                has_num = True
            else:
                terms.append(term)
        if has_num:
            terms.append(num)
        return Sum(terms)


class Prod(_CoreProdTemplate):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if Num.is_num(factor):
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

    def expand(self):
        to_expand = []
        for factor in self.factors:
            factor = factor.expand()
            if isinstance(factor, Sum):
                to_expand.append(factor.terms)
            else:
                to_expand.append([factor])
        return Sum([Prod(term) for term in product(*to_expand)])

    def factorize(self):
        return Prod([factor.factorize() for factor in self.factors])

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

    def substitute_vars(self, var_map):
        return Prod([term.substitute_vars(var_map) for term in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])
    
    @cached_property
    def isnum(self):
        for factor in self.factors:
            if not factor.isnum:
                return False
        return True

    def copy(self):
        return Prod([factor.copy() for factor in self.factors])
    
    def eval_nums(self):
        num = one
        factors = []
        has_num = False
        for factor in self.factors:
            if factor.isnum:
                num += factor.eval_nums()
                has_num = True
            else:
                factors.append(factor)
        if has_num:
            factors.append(num)
        return Prod(factors)


class Frac(_CoreFracTemplate):
    def __init__(self, numer, denom):
        self.numer = Num(numer) if Num.is_num(numer) else numer
        self.denom = Num(denom) if Num.is_num(denom) else denom

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        numers = self.numer.decomp()
        denoms = self.denom.decomp()
        numers.subtract(denoms)
        return numers

    def expand(self):
        return Frac(self.numer.expand(), self.denom.expand())

    def factorize(self):
        return Frac(self.numer.factorize(), self.denom.factorize())

    def simplify(self):
        """Returns the fraction with simplified numerator and denominator"""
        numer = self.numer.simplify().decomp()
        denom = self.denom.simplify().decomp()
        numer.subtract(denom)
        return decomp2prod(numer).simplify()

    def substitute_vars(self, var_map):
        return Frac(self.numer.substitute_vars(var_map), self.denom.substitute_vars(var_map))

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    @cached_property
    def isnum(self):
        return self.numer.isnum and self.denom.isnum

    def copy(self):
        return Frac(self.numer.copy(), self.denom.copy())

    def eval_nums(self):
        return self.numer.eval_nums() / self.denom.eval_nums()


class Exp(_CoreExpTemplate):
    def __init__(self, base, power):
        self.base = Num(base) if Num.is_num(base) else base
        self.power = Num(power) if Num.is_num(power) else power

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        if isinstance(self.power, Num):
            return Counter({self.base: self.power})
        return Counter({self: 1})

    def expand(self):
        if isinstance(self.power, Num) and int(self.power) == self.power and self.power > 0:
            return Prod([self.base] * int(self.power)).expand()
        return self

    def factorize(self):
        return Exp(self.base.factorize(), self.power.factorize())

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
            if base == int(base) and power == int(power) and power > 0:
                return base ** power
            result = base ** power
            if result == int(result):
                return result
        return Exp(base, power)

    def substitute_vars(self, var_map):
        return self.base.substitute_vars(var_map) ** self.power.substitute_vars(var_map)

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    @cached_property
    def isnum(self):
        return self.base.isnum and self.power.isnum

    def copy(self):
        return Exp(self.base.copy(), self.power.copy())

    def eval_nums(self):
        return self.base.eval_nums() ** self.power.eval_nums()


class Eqn(_CoreEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = Num(lhs) if Num.is_num(lhs) else lhs
        self.rhs = Num(rhs) if Num.is_num(rhs) else rhs

    def expand(self):
        return Eqn(self.lhs.expand(), self.rhs.expand())

    def factorize(self):
        return Eqn(self.lhs.factorize(), self.rhs.factorize())

    def simplify(self):
        return Eqn(self.lhs.simplify(), self.rhs.simplify())

    def swap(self):
        return Eqn(self.rhs, self.lhs)

    def substitute_vars(self):
        pass

    @cached_property
    def get_vars(self):
        return self.lhs.get_vars | self.rhs.get_vars

    def copy(self):
        return Eqn(self.lhs.copy, self.rhs.copy)


class Func: # TODO this has been on todo for the longest time
    def __init__(self):
        pass


CORE_EXPR = (Num, Var, Sum, Prod, Frac, Exp)
CORE_TYPES = (Num, Var, Sum, Prod, Frac, Exp, Eqn)


def decomp2prod(decomp: Counter) -> Prod:
    return Prod([Exp(base, power) for base, power in decomp.items()])


if __name__ == '__main__':
    x = Var('x')
    y = Var('y')

    expr = Exp(15, 2)
    print(expr.simplify())