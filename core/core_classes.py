from itertools import product
from core.num import *

__all__ = ['Var', 'Sum', 'Prod', 'Frac', 'Exp', 'Eqn',
           'Undefined', 'Indeterminate', 'NoRealSol']

# TODO check sub for CoreTemplate and SumTemplate
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
        return Sum([-other, self])

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
        return [self]

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
        return Sum([other + -self])

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


class _UndefinedType:
    def __str__(self):
        return 'Undefined'

    def __repr__(self):
        return 'Undefined'


class _IndeterminateType:
    def __str__(self):
        return 'Indeterminate'

    def __repr__(self):
        return 'Indeterminate'


class _NoRealSol:
    def __str__(self):
        return 'No real solution'

    def __repr__(self):
        return 'No real solution'


class Var(_CoreVarTemplate):
    def __init__(self, symbol):
        self.sym = symbol


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
        decomp = [term.group().decomp() for term in self.terms]
        unique = {}
        for term in decomp:
            # Multiplying constants in each term to get coefficient
            coeff = one
            for i, factor in reversed(list(enumerate(term))):
                if Num.isnum(factor):
                    coeff *= term.pop(i)
            # Accumulating coefficients of like terms
            term = Prod(term) # term was a list
            if term in unique.keys():
                unique[term] += coeff
            else:
                unique[term] = coeff
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
        decomp = []
        for factor in self.factors:
            decomp.extend(factor.decomp())
        return decomp

    def group(self):
        """Collects like factors into exponents"""
        unique = {}
        const = 1
        for factor in self.factors:
            # Multiplying to get constant
            if isinstance(factor, Num):
                const *= factor
                continue
            # Accumulating powers of like factors
            if isinstance(factor, Exp):
                if factor.base in unique.keys():
                    unique[factor.base] += factor.power
                else:
                    unique[factor.base] = factor.power
            else:
                if factor in unique.keys():
                    unique[factor] += 1
                else:
                    unique[factor] = 1
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

    # def to_frac(self):
    #     numers, denoms = [], []
    #     for factor in self.factors:
    #         if isinstance(factor, Frac):
    #             numers.append(factor.numer)
    #             denoms.append(factor.denom)
    #         elif isinstance(factor, Exp):
    #             if Num.isnum(factor.power):
    #                 if factor.power < 0:
    #                     denoms.append(Exp(factor.base, -factor.power))
    #                 else:
    #                     numers.append(factor)
    #             else:
    #                 numers.append(factor)
    #         else:
    #             numers.append(factor)
    #     return Frac(Prod(numers), Prod(denoms))


class Frac(_CoreFracTemplate):
    def __init__(self, numer, denom):
        self.numer = Num(numer) if Num.isnum(numer) else numer
        self.denom = Num(denom) if Num.isnum(denom) else denom

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        numers = self.numer.decomp()
        denoms = self.denom.decomp()
        denoms = [Exp(denom, neg_one) for denom in denoms]
        return numers + denoms

    def simplify(self):
        """Returns the fraction in its simplest form"""
        # Resolving nested fractions
        numer = self.numer.simplify()
        denom = self.denom.simplify()
        if isinstance(numer, Frac) and isinstance(denom, Frac):
            numer_flat = numer.numer * denom.denom
            denom_flat = numer.denom * denom.numer
        elif isinstance(numer, Frac) and not isinstance(denom, Frac):
            numer_flat = numer.numer
            denom_flat = numer.denom * denom
        elif not isinstance(numer, Frac) and isinstance(denom, Frac):
            numer_flat = numer * denom.denom
            denom_flat = denom.numer
        else:
            numer_flat = numer
            denom_flat = denom

        # Decomposing numerator and denominator (always factorising)
        if isinstance(numer_flat, Sum):
            numer_flat = numer_flat.factorise()
        if isinstance(denom_flat, Sum):
            denom_flat = denom_flat.factorise()
        numer_decomp = numer_flat.decomp()
        denom_decomp = denom_flat.decomp()

        # Removing common factors
        for factor in reversed(numer_decomp):
            if factor in denom_decomp:
                numer_decomp.remove(factor)
                denom_decomp.remove(factor)
        numer_out = Prod(numer_decomp).simplify()
        denom_out = Prod(denom_decomp).simplify()
        if denom_out == zero:
            return Undefined
        if numer_out == zero and denom_out != zero:
            return zero
        if numer_out != zero and denom_out == one:
            return numer_out
        return numer_out / denom_out

    def expand(self):
        """Returns an expansion of the numerator and denominator"""
        return self.numer.expand() / self.denom.expand()

    # def to_prod(self):
    #     numer_prod = self.numer.decomp()
    #     denom_prod = self.denom.decomp()
    #     denom_prod = [Exp(factor, neg_one) for factor in denom_prod]
    #     return Prod(numer_prod + denom_prod)


class Exp(_CoreExpTemplate):
    def __init__(self, base, power):
        self.base = Num(base) if Num.isnum(base) else base
        self.power = Num(power) if Num.isnum(power) else power

    def decomp(self):
        """Decomposes the expression into its constituent factors"""
        i, f = divmod(self.power, one)
        if i > zero:
            output = [self.base for _ in range(int(i))]
        else:
            output = [Exp(self.base, neg_one) for _ in range(-int(i))]
        if f != zero:
            output.append(Exp(self.base, f))
        return output

    def simplify(self):
        """Simplifies the expression"""
        power = self.power.simplify()
        base = self.base.simplify()
        if isinstance(base, Exp):
            return Exp(base.base, base.power * power).simplify()
        if base == one or (base != one and base != zero and power == zero):
            return one
        if base == zero and power != zero:
            return zero
        if base != zero and base != one and power == one:
            return base
        if base == zero and power == zero:
            return Undefined
        return base ** power

    def expand(self):
        """Returns an expansion of the exponential"""
        decomp = self.decomp()
        if len(decomp) == 1:
            return decomp[0]
        return Prod(decomp).expand()

    # def to_prod(self):
    #     return Prod(self.decomp())


class Eqn(_CoreEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = Num(lhs) if Num.isnum(lhs) else lhs
        self.rhs = Num(rhs) if Num.isnum(rhs) else rhs

    def simplify(self):
        lhs = self.lhs.simplify()
        rhs = self.rhs.simplify()
        return Eqn(lhs, rhs)

    def isequal(self):
        return self.lhs == self.rhs

    def swap(self):
        return Eqn(self.rhs, self.lhs)


Undefined = _UndefinedType()
Indeterminate = _IndeterminateType()
NoRealSol = _NoRealSol()

if __name__ == '__main__':
    x = Var('x')
    expr = (x+1)**1 * (x+1) ** 1
    expr = expr.expand().simplify()
    print(expr)