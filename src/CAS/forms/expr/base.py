from functools import cached_property

from .registry import FORMS


__all__ = ['FormExprBase',
           'FormConstBase', 'FormNumBase', 'FormVarBase', 'FormWildBase',
           'FormSumBase', 'FormProdBase', 'FormFracBase', 'FormExpBase']


class FormExprBase:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    def __add__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum([self] + other.terms)
        return FORMS.sum((self, other))

    def __radd__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum(other.terms + [self])
        return FORMS.sum((other, self))

    def __sub__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum([self] + (-other).terms)
        return FORMS.sum((self, -other))

    def __rsub__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum((-other).terms + [self])
        return FORMS.sum((-other, self))

    def __mul__(self, other):
        if isinstance(other, FORMS.prod):
            return FORMS.prod([self] + other.factors)
        return FORMS.prod((self, other))

    def __rmul__(self, other):
        if isinstance(other, FORMS.prod):
            return FORMS.prod(other.factors + [self])
        return FORMS.prod((other, self))

    def __truediv__(self, other):
        return FORMS.frac(self, other)

    def __rtruediv__(self, other):
        return FORMS.frac(other, self)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Modulo functionality is not available")
        return FORMS.exp(self, power)

    def __rpow__(self, other):
        return FORMS.exp(other, self)

    def __neg__(self):
        return self * FORMS.neg_one

    def __pos__(self):
        return self


    @cached_property
    def isconst(self):
        return False

    def group_consts(self):
        return self

    @cached_property
    def get_consts(self):
        return set()

    @cached_property
    def get_vars(self):
        return set()

    def substitute_consts(self, const_map):
        return self


class FormNumBase(FormExprBase):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"FormNum({self.value})"

    def __hash__(self):
        # hash('-1') = 357669246384252548
        h = hash(self.value)
        return h if h != -1 else 357669246384252548

    def __neg__(self):
        return FORMS.num(-self.value)


class FormConstBase(FormExprBase):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormConst('{self.sym}')"

    def __hash__(self):
        return hash(('FormConst', self.sym))


class FormVarBase(FormExprBase):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormVar('{self.sym}')"

    def __hash__(self):
        return hash(('FormVar', self.sym))


class FormWildBase(FormExprBase):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormWild('{self.sym}')"

    def __hash__(self):
        return hash(('FormWild', self.sym))


class FormSumBase(FormExprBase):
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
        if isinstance(other, FORMS.sum):
            return FORMS.sum(self.terms + other.terms)
        return FORMS.sum(self.terms + [other])

    def __radd__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum(other.terms + self.terms)
        return FORMS.sum([other] + self.terms)

    def __iadd__(self, other):
        if isinstance(other, FORMS.sum):
            self.terms.extend(other.terms)
        self.terms.append(other)
        return self

    def __sub__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum(self.terms + (-other).terms)
        return FORMS.sum(self.terms + [-other])

    def __rsub__(self, other):
        if isinstance(other, FORMS.sum):
            return FORMS.sum(other.terms + (-self).terms)
        return FORMS.sum([other] + (-self).terms)

    def __isub__(self, other):
        self.terms.append(-other)
        return self


class FormProdBase(FormExprBase):
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
        if isinstance(other, FORMS.prod):
            return FORMS.prod(self.factors + other.factors)
        return FORMS.prod(self.factors + [other])

    def __rmul__(self, other):
        if isinstance(other, FORMS.prod):
            return FORMS.prod(other.factors + self.factors)
        return FORMS.prod([other] + self.factors)

    def __imul__(self, other):
        if isinstance(other, FORMS.prod):
            self.factors.extend(other.factors)
        self.factors.append(other)
        return self


class FormFracBase(FormExprBase):
    def __str__(self):
        return f'({str(self.numer)} / {str(self.denom)})'

    def __repr__(self):
        return f'FormFrac({repr(self.numer)}, {repr(self.denom)})'

    def __hash__(self):
        return hash(('FormFrac', self.numer, self.denom))


class FormExpBase(FormExprBase):
    def __str__(self):
        return f'({str(self.base)} ^ {str(self.power)})'

    def __repr__(self):
        return f'FormExp({repr(self.base)}, {repr(self.power)})'

    def __hash__(self):
        return hash(('FormExp', self.base, self.power))