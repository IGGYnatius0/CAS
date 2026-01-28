from decimal import Decimal

from core.core_classes import *
from core.core_classes import neg_one, zero, one

# TODO make match return dict of variables and their values

class FormNum(Decimal):
    def match(self, expr, var_map={}):
        return expr == self

    @classmethod
    def isnum(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"FormNum({str(self)})"

    def __hash__(self):
        return hash(('FormNum', super().__hash__()))


class FormTemplate:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    def __add__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum([self] + other.terms)
        return FormSum((self, other))

    def __radd__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum(other.terms + [self])
        return FormSum((other, self))

    def __sub__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum([self] + (-other).terms)
        return FormSum((self, -other))

    def __rsub__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum((-other).terms + [self])
        return FormSum((-other, self))

    def __mul__(self, other):
        if isinstance(other, FormProdTemplate):
            return FormProd([self] + other.factors)
        return FormProd((self, other))

    def __rmul__(self, other):
        if isinstance(other, FormProdTemplate):
            return FormProd(other.factors + [self])
        return FormProd((other, self))

    def __truediv__(self, other):
        return FormFrac(self, other)

    def __rtruediv__(self, other):
        return FormFrac(other, self)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return FormExp(self, power)

    def __rpow__(self, other):
        return FormExp(other, self)

    def __neg__(self):
        return self * neg_one

    def __pos__(self):
        return self


class FormConstTemplate(FormTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormConst('{self.sym}')"

    def __hash__(self):
        return hash(('FormConst', self.sym))


class FormVarTemplate(FormTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormVar('{self.sym}')"

    def __hash__(self):
        return hash(('FormVar', self.sym))


class FormSumTemplate(FormTemplate):
    def __str__(self):
        terms = [str(term) for term in self.terms]
        return f'({" + ".join(terms)})'

    def __repr__(self):
        terms = [repr(term) for term in self.terms]
        return f'FormSum([{", ".join(terms)}])'

    def __hash__(self):
        hashes = [hash(term) for term in self.terms]
        return hash(('FormSum',) + tuple(sorted(hashes)))

    def __add__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum(self.terms + other.terms)
        return FormSum(self.terms + [other])

    def __radd__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum(other.terms + self.terms)
        return FormSum([other] + self.terms)

    def __iadd__(self, other):
        if isinstance(other, FormSumTemplate):
            self.terms.extend(other.terms)
        self.terms.append(other)
        return self

    def __sub__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum(self.terms + (-other).terms)
        return FormSum(self.terms + [-other])

    def __rsub__(self, other):
        if isinstance(other, FormSumTemplate):
            return FormSum(other.terms + (-self).terms)
        return FormSum([other] + (-self).terms)

    def __isub__(self, other):
        self.terms.append(-other)
        return self


class FormProdTemplate(FormTemplate):
    def __str__(self):
        factors = [str(factor) for factor in self.factors]
        return f'({" * ".join(factors)})'

    def __repr__(self):
        factors = [repr(factor) for factor in self.factors]
        return f'FormProd([{", ".join(factors)}])'

    def __hash__(self):
        hashes = [hash(factor) for factor in self.factors]
        return hash(('FormProd',) + tuple(sorted(hashes)))

    def __mul__(self, other):
        if isinstance(other, FormProdTemplate):
            return FormProd(self.factors + other.factors)
        return FormProd(self.factors + [other])

    def __rmul__(self, other):
        if isinstance(other, FormProdTemplate):
            return FormProd(other.factors + self.factors)
        return FormProd([other] + self.factors)

    def __imul__(self, other):
        if isinstance(other, FormProdTemplate):
            self.factors.extend(other.factors)
        self.factors.append(other)
        return self


class FormFracTemplate(FormTemplate):
    def __str__(self):
        return f'({str(self.numer)} / {str(self.denom)})'

    def __repr__(self):
        return f'FormFrac({repr(self.numer)}, {repr(self.denom)})'

    def __hash__(self):
        return hash(('FormFrac', self.numer, self.denom))


class FormExpTemplate(FormTemplate):
    def __str__(self):
        return f'({str(self.base)} ^ {str(self.power)})'

    def __repr__(self):
        return f'FormExp({repr(self.base)}, {repr(self.power)})'

    def __hash__(self):
        return hash(('FormExp', self.base, self.power))


class FormEqnTemplate:
    def __eq__(self, other):
        if not isinstance(other, FormEqnTemplate):
            return False
        return ((self.lhs == other.lhs and self.rhs == other.rhs) or
                (self.lhs == other.rhs and self.rhs == other.lhs))

    def __add__(self, other):
        return FormEqn(self.lhs + other.lhs, self.rhs + other.rhs)

    def __radd__(self, other):
        return FormEqn(other.lhs + self.lhs, other.rhs + self.rhs)

    def __iadd__(self, other):
        self.rhs += other.rhs
        self.lhs += other.lhs
        return self

    def __sub__(self, other):
        return FormEqn(self.lhs - other.lhs, self.rhs - other.rhs)

    def __rsub__(self, other):
        return FormEqn(other.lhs - self.lhs, other.rhs - self.rhs)

    def __isub__(self, other):
        self.rhs -= other.rhs
        self.lhs -= other.lhs
        return self

    def __mul__(self, other):
        return FormEqn(self.lhs * other.lhs, self.rhs * other.rhs)

    def __rmul__(self, other):
        return FormEqn(other.lhs * self.lhs, other.rhs * self.rhs)

    def __imul__(self, other):
        self.rhs *= other.rhs
        self.lhs *= other.lhs
        return self

    def __truediv__(self, other):
        return FormEqn(self.lhs / other.lhs, self.rhs / other.rhs)

    def __rtruediv__(self, other):
        return FormEqn(other.lhs / self.lhs, other.rhs / self.rhs)

    def __itruediv__(self, other):
        self.rhs /= other.rhs
        self.lhs /= other.lhs
        return self

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return FormEqn(self.lhs ** power.lhs, self.rhs ** power.rhs)

    def __rpow__(self, other):
        return FormEqn(other.lhs ** self.lhs, other.rhs ** self.rhs)

    def __ipow__(self, other):
        self.rhs **= other.rhs
        self.lhs **= other.lhs
        return self

    def __str__(self):
        return f'{str(self.lhs)} = {str(self.rhs)}'

    def __repr__(self):
        return f'FormEqn({repr(self.lhs)}, {repr(self.rhs)})'

    def __hash__(self):
        return hash(('FormEqn', self.lhs, self.rhs))


class FormConst(FormConstTemplate):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map={}):
        return isinstance(expr, Decimal)


class FormVar(FormVarTemplate):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map={}):
        if not isinstance(expr, Var):
            return False
        if expr.sym in var_map.keys():
            return var_map[expr.sym] == self.sym
        var_map[expr.sym] = self.sym
        return True


class FormSum(FormSumTemplate):
    def __init__(self, terms):
        self.terms = []
        for term in terms:
            if FormNum.isnum(term):
                self.terms.append(FormNum(term))
            elif term is None or term == []:
                continue
            else:
                self.terms.append(term)
        # Empty case
        if not self.terms:
            self.terms = [zero]
        # TODO functionality for multiple and repeated terms

    def match(self, expr, var_map={}):
        # Non-Sum case
        if not isinstance(expr, Sum):
            return self.match(Sum([expr]), var_map)
        # Others
        if len(expr.terms) > len(self.terms):
            return False
        expr_terms = expr.terms.copy()
        form_terms = self.terms
        # Pad expr with +0 until length is equal
        pad = [zero] * (len(form_terms) - len(expr_terms))
        expr_terms.extend(pad)
        for form in form_terms:
            # Check if form term matches any remaining expr terms
            for i, expr in enumerate(expr_terms):
                if not form.match(expr, var_map):
                    continue
                # If match found move on to next form term
                expr_terms.pop(i)
                break
            else:
                return False
        return True


class FormProd(FormProdTemplate):
    def __init__(self, factors):
        self.factors = []
        for factor in factors:
            if FormNum.isnum(factor):
                self.factors.append(FormNum(factor))
            elif factor is None or factor == []:
                continue
            else:
                self.factors.append(factor)
        # Empty case
        if not self.factors:
            self.factors = [one]

    def match(self, expr, var_map={}):
        # 0 case
        if expr == zero:
            return any([factor.match(zero, var_map) for factor in self.factors])
        # Non-Prod case
        if not isinstance(expr, Prod):
            return self.match(Prod([expr]), var_map)
        # Others
        if len(expr.factors) > len(self.factors):
            return False
        expr_factors = expr.factors.copy()
        form_factors = self.factors
        # Pad expr with *1 until length is equal
        pad = [one] * (len(form_factors) - len(expr_factors))
        expr_factors.extend(pad)
        for form in form_factors:
            # Check if form factor matches any remaining expr factor
            for i, expr in enumerate(expr_factors):
                if not form.match(expr, var_map):
                    continue
                # If match found move on to next form factor
                expr_factors.pop(i)
                break
            else:
                return False
        return True


class FormFrac(FormFracTemplate):
    def __init__(self, numer, denom):
        self.numer = FormNum(numer) if FormNum.isnum(numer) else numer
        self.denom = FormNum(denom) if FormNum.isnum(denom) else denom

    def match(self, expr, var_map={}):
        # Non-Frac case
        if not isinstance(expr, Frac):
            return self.match(expr / one, var_map)
        # Others
        numer_match = self.numer.match(expr.numer, var_map)
        if not numer_match:
            return False
        denom_match = self.denom.match(expr.denom, var_map)
        if not denom_match:
            return False
        return True


class FormExp(FormExpTemplate):
    def __init__(self, base, power):
        self.base = FormNum(base) if FormNum.isnum(base) else base
        self.power = FormNum(power) if FormNum.isnum(power) else power

    def match(self, expr, var_map={}):
        # 1 and 0 case
        if expr == one or expr == zero:
            base1 = self.base.match(one, var_map)
            power0 = self.power.match(zero, var_map)
            return base1 or power0
        # Non-Exp case
        if not isinstance(expr, Exp):
            return self.match(Exp(expr, one), var_map)
        # Exp case
        base_match = self.base.match(expr.base, var_map)
        if not base_match:
            return False
        power_match = self.power.match(expr.power, var_map)
        if not power_match:
            return False
        return True


class FormEqn(FormEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = FormNum(lhs) if FormNum.isnum(lhs) else lhs
        self.rhs = FormNum(rhs) if FormNum.isnum(rhs) else rhs

    def match(self, expr, var_map={}):
        if not isinstance(expr, Eqn):
            return False
        return ((self.lhs.match(expr.lhs, var_map) and self.rhs.match(expr.rhs, var_map)) or
                (self.lhs.match(expr.rhs, var_map) and self.rhs.match(expr.lhs, var_map)))


if __name__ == '__main__':
    x = Var('x')
    y = FormVar('y')
    a = FormConst('a')
    b = FormConst('b')
    c = FormConst('c')
    expr = x**2
    form = a*y**2 + b*y + c
    print(expr)
    print(form)
    print(form.match(expr))
