from decimal import Decimal
from itertools import product, chain
from functools import cached_property
from collections import Counter

from core.classes import *

# READ BEFORE ADDING!!
# Every form class has to implement the following methods: (might use ABCs next time)
# __hash__, match, isconst, group_consts, get_consts, get_vars, substitute

__all__ = ['FormNum', 'FormConst', 'FormVar', 'FormSum', 'FormProd', 'FormFrac', 'FormExp', 'FormWild', 'match']


class _FormTemplate:
    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return hash(self) == hash(other)

    def __add__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum([self] + other.terms)
        return FormSum((self, other))

    def __radd__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum(other.terms + [self])
        return FormSum((other, self))

    def __sub__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum([self] + (-other).terms)
        return FormSum((self, -other))

    def __rsub__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum((-other).terms + [self])
        return FormSum((-other, self))

    def __mul__(self, other):
        if isinstance(other, _FormProdTemplate):
            return FormProd([self] + other.factors)
        return FormProd((self, other))

    def __rmul__(self, other):
        if isinstance(other, _FormProdTemplate):
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


def _num_check(func):
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        if FormNum.isnum(f):
            return FormNum(f)
        return f
    return wrapper


class _FormNumTemplate(Decimal):
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


class _FormConstTemplate(_FormTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormConst('{self.sym}')"

    def __hash__(self):
        return hash(('FormConst', self.sym))


class _FormVarTemplate(_FormTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormVar('{self.sym}')"

    def __hash__(self):
        return hash(('FormVar', self.sym))


class _FormWildTemplate(_FormTemplate):
    def __str__(self):
        return self.sym

    def __repr__(self):
        return f"FormWild('{self.sym}')"

    def __hash__(self):
        return hash(('FormWild', self.sym))


class _FormSumTemplate(_FormTemplate):
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
        if isinstance(other, _FormSumTemplate):
            return FormSum(self.terms + other.terms)
        return FormSum(self.terms + [other])

    def __radd__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum(other.terms + self.terms)
        return FormSum([other] + self.terms)

    def __iadd__(self, other):
        if isinstance(other, _FormSumTemplate):
            self.terms.extend(other.terms)
        self.terms.append(other)
        return self

    def __sub__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum(self.terms + (-other).terms)
        return FormSum(self.terms + [-other])

    def __rsub__(self, other):
        if isinstance(other, _FormSumTemplate):
            return FormSum(other.terms + (-self).terms)
        return FormSum([other] + (-self).terms)

    def __isub__(self, other):
        self.terms.append(-other)
        return self


class _FormProdTemplate(_FormTemplate):
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
        if isinstance(other, _FormProdTemplate):
            return FormProd(self.factors + other.factors)
        return FormProd(self.factors + [other])

    def __rmul__(self, other):
        if isinstance(other, _FormProdTemplate):
            return FormProd(other.factors + self.factors)
        return FormProd([other] + self.factors)

    def __imul__(self, other):
        if isinstance(other, _FormProdTemplate):
            self.factors.extend(other.factors)
        self.factors.append(other)
        return self


class _FormFracTemplate(_FormTemplate):
    def __str__(self):
        return f'({str(self.numer)} / {str(self.denom)})'

    def __repr__(self):
        return f'FormFrac({repr(self.numer)}, {repr(self.denom)})'

    def __hash__(self):
        return hash(('FormFrac', self.numer, self.denom))


class _FormExpTemplate(_FormTemplate):
    def __str__(self):
        return f'({str(self.base)} ^ {str(self.power)})'

    def __repr__(self):
        return f'FormExp({repr(self.base)}, {repr(self.power)})'

    def __hash__(self):
        return hash(('FormExp', self.base, self.power))


def eqn_typecheck(func):
    def wrapper(self, other):
        if not isinstance(other, _FormEqnTemplate):
            return func(self, FormEqn(other, other))
        return func(self, other)
    return wrapper


class _FormEqnTemplate:
    def __str__(self):
        return f'{str(self.lhs)} = {str(self.rhs)}'
    
    def __repr__(self):
        return f'{repr(self.lhs)} = {repr(self.rhs)}'
    
    def __hash__(self):
        return hash(('FormEqn', self.lhs, self.rhs))

    @eqn_typecheck
    def __add__(self, other):
        return FormEqn(self.lhs + other.lhs, self.rhs + other.rhs)
    
    @eqn_typecheck
    def __radd__(self, other):
        return FormEqn(other.lhs + self.lhs, other.rhs + self.rhs)  # Fixed: was self.lhs
    
    @eqn_typecheck
    def __iadd__(self, other):
        self.lhs += other.lhs
        self.rhs += other.rhs
        return self
    
    @eqn_typecheck
    def __sub__(self, other):
        return FormEqn(self.lhs - other.lhs, self.rhs - other.rhs)
    
    @eqn_typecheck
    def __rsub__(self, other):
        return FormEqn(other.lhs - self.lhs, other.rhs - self.rhs)
    
    @eqn_typecheck
    def __isub__(self, other):
        self.lhs -= other.lhs
        self.rhs -= other.rhs
        return self
    
    @eqn_typecheck
    def __mul__(self, other):
        return FormEqn(self.lhs * other.lhs, self.rhs * other.rhs)
    
    @eqn_typecheck
    def __rmul__(self, other):
        return FormEqn(other.lhs * self.lhs, other.rhs * self.rhs)
    
    @eqn_typecheck
    def __imul__(self, other):
        self.lhs *= other.lhs
        self.rhs *= other.rhs
        return self
    
    @eqn_typecheck
    def __truediv__(self, other):
        return FormEqn(self.lhs / other.lhs, self.rhs / other.rhs)
    
    @eqn_typecheck
    def __rtruediv__(self, other):
        return FormEqn(other.lhs / self.lhs, other.rhs / self.rhs)
    
    @eqn_typecheck
    def __itruediv__(self, other):
        self.lhs /= other.lhs
        self.rhs /= other.rhs
        return self
    
    @eqn_typecheck
    def __pow__(self, other):
        return FormEqn(self.lhs ** other.lhs, self.rhs ** other.rhs)
    
    @eqn_typecheck
    def __rpow__(self, other):
        return FormEqn(other.lhs ** self.lhs, other.rhs ** self.rhs)
    
    @eqn_typecheck
    def __ipow__(self, other):
        self.lhs **= other.lhs
        self.rhs **= other.rhs
        return self


class SingleConstraint:
    def __init__(self, form=None, value=None, var_map=None):
        self.form = form
        self.value = value
        self.var_map = var_map

    def sort_matches(self):
        """Sorts self.matches by increasing number of constraints"""
        return [(self,)]

    def get_constraints(self):
        """Returns a generator of all possible combinations of constraints"""
        yield (self,)
        return

    def simplify(self):
        prev_form = None
        while self.form != prev_form:
            prev_form = self.form
            if isinstance(self.form, FormSum):
                self.simplify_sum()
            elif isinstance(self.form, FormProd):
                self.simplify_prod()
            elif isinstance(self.form, FormFrac):
                self.simplify_frac()
            elif isinstance(self.form, FormExp):
                self.simplify_exp()
            if isinstance(self.form, FormSum) and len(self.form.terms) == 1:
                self.form = self.form.terms[0]
            elif isinstance(self.form, FormProd) and len(self.form.factors) == 1:
                self.form = self.form.factors[0]

    def simplify_sum(self):
        for i, term in enumerate(self.form.terms):
            if isinstance(term, Decimal):
                self.value -= Num(term)
                self.form.terms.pop(i)
                return

    def simplify_prod(self):
        for i, factor in enumerate(self.form.factors):
            if isinstance(factor, Decimal):
                self.value /= Num(factor) # FIXME possible division by zero
                self.form.factors.pop(i)
                return

    def simplify_frac(self):
        if isinstance(self.form.numer, Decimal):
            self.value = Num(self.form.numer) / self.value
            self.form = self.form.denom
        elif isinstance(self.form.denom, Decimal):
            self.value *= Num(self.form.denom)
            self.form = self.form.numer

    def simplify_exp(self):
        if isinstance(self.form.base, Decimal):
            # TODO logarithm
            pass
        elif isinstance(self.form.power, Decimal):
            self.value **= one / Num(self.form.power)
            self.form = self.form.base

    def __bool__(self):
        return True

    def __repr__(self):
        return f'({str(self.form)}: {str(self.value)})'

    def __str__(self):
        return f'({str(self.form)}: {str(self.value)})'


class MultiConstraint:
    def __init__(self, size):
        self.size = size
        self.matches = [[False] * size for _ in range(size)]
        self.nmatches = [0] * size

    def check_validity(self):
        """Checks if every row and column of self.matches has at least 1 constraint"""
        for form_match in self.matches:
            if not any(form_match):
                return False
        for i in range(self.size):
            if not any(value_match[i] for value_match in self.matches):
                return False
        return True

    def sort_matches(self):
        """Sorts self.matches by increasing number of constraints"""
        sorted_matches = sorted(zip(self.nmatches, self.matches), key=lambda x: x[0])
        self.nmatches, self.matches = zip(*sorted_matches)

    def get_constraints(self):
        if not self.check_validity():
            yield ()
            return

        if self.size == 1:
            yield from self.matches[0][0].get_constraints()
            return

        self.sort_matches()

        # Getting all valid constraints in the first row
        idxs = []
        for i, constr in enumerate(self.matches[0]):
            if not constr or \
                    (isinstance(constr, SingleConstraint) and constr.form is None):
                continue
            idxs.append(i)

        # Remove the column where each constraint identified above is
        for idx in idxs:
            new_matches = []
            for row in self.matches[1:]:
                new_row = []
                for i, constr in enumerate(row):
                    if i == idx:
                        continue
                    new_row.append(constr)
                new_matches.append(new_row)

            new_mc = MultiConstraint(0)
            new_mc.size = self.size - 1
            new_mc.matches = new_matches
            new_mc.nmatches = [n - 1 for n in self.nmatches[1:]]

            constrs1 = self.matches[0][idx].get_constraints()
            constrs2 = new_mc.get_constraints()
            for c1, c2 in product(constrs1, constrs2):
                yield chain.from_iterable((c1, c2))

    def __setitem__(self, idx, item):
        self.matches[idx[0]][idx[1]] = item
        self.nmatches[idx[0]] += 1

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            return self.matches[idx[0]][idx[1]]
        return self.matches[idx]

    def __bool__(self):
        return True


class FormNum(_FormNumTemplate):
    def __init__(self, value, *args, **kwargs):
        Decimal.__init__(str(value), *args, **kwargs)

    def match(self, expr, var_map):
        if expr == self:
            return SingleConstraint(var_map=var_map)
        return False

    @cached_property
    def isconst(self):
        return True

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

    @classmethod
    def isnum(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"FormNum({str(self)})"

    def __hash__(self):
        return hash(('FormNum', super().__hash__()))


class FormConst(_FormConstTemplate):
    # TODO ranges eg FormConst('a', 'a>0')
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map):
        if not isinstance(expr, Num):
            return False
        return SingleConstraint(self, expr, var_map)

    @cached_property
    def isconst(self):
        return True

    def group_consts(self):
        return self

    @cached_property
    def get_consts(self):
        return {self}

    @cached_property
    def get_vars(self):
        return set()

    def substitute_consts(self, const_map):
        if self in const_map:
            return FormNum(const_map[self])
        return self


class FormVar(_FormVarTemplate):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map):
        if not isinstance(expr, Var):
            return False
        if self in var_map:
            if var_map[self] == expr:
                return SingleConstraint(self, expr, var_map)
            return False
        if expr in var_map.values():
            return False
        var_map[self] = expr
        return SingleConstraint(self, expr, var_map)

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
        return {self}

    def substitute_consts(self, const_map):
        return self


class FormWild(_FormWildTemplate):
    # TODO type restrictions
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map):
        if self in var_map:
            if var_map[self] == expr:
                return SingleConstraint(self, expr, var_map)
            return False
        var_map[self] = expr
        return SingleConstraint(self, expr, var_map)

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
        return {self}
    
    def substitute_consts(self, const_map):
        return self


class FormSum(_FormSumTemplate):
    def __init__(self, terms):
        # TODO functionality for summations/large number of terms
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

    def match(self, expr, var_map):
        if isinstance(expr, Num):
            if self.isconst:
                return SingleConstraint(self, expr, var_map.copy())
            if expr == zero:
                # FormSum can match zero if all terms can match zero
                zeros = [zero] * len(self.terms)
                return self.match(Sum(zeros), var_map.copy())
            return False
        if isinstance(expr, Sum) and len(self.terms) != len(expr.terms):
            if len(expr.terms) > len(self.terms):
                return False
            # Padding by +0
            zeros = [zero] * (len(self.terms) - len(expr.terms))
            terms = expr.terms + zeros
            return self.match(Sum(terms), var_map.copy())
        if not isinstance(expr, Sum):
            # Padding by +0
            zeros = [zero] * (len(self.terms)-1)
            return self.match(Sum([expr] + zeros), var_map.copy())
        matches = MultiConstraint(len(self.terms))
        for i, ft in enumerate(self.terms):
            for j, et in enumerate(expr.terms):
                match = ft.match(et, var_map.copy())
                if match:
                    matches[i, j] = match
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        for term in self.terms:
            if not term.isconst:
                return False
        return True

    def group_consts(self):
        """Groups all constants in this FormSum into a single FormSum"""
        terms = [term.group_consts() for term in self.terms]
        temp = FormSum(terms)
        if temp.isconst:
            return temp
        consts = []
        for i, term in reversed(list(enumerate(terms))):
            if term.isconst:
                consts.append(terms.pop(i))
        if len(consts) == 1:
            terms.append(consts[0])
        elif len(consts) > 1:
            terms.append(FormSum(consts))
        return FormSum(terms)

    @cached_property
    def get_consts(self):
        return set.union(*[term.get_consts for term in self.terms])

    @cached_property
    def get_vars(self):
        return set.union(*[term.get_vars for term in self.terms])
    
    def substitute_consts(self, const_map):
        terms = []
        num = zero
        for term in self.terms:
            sub = term.substitute_consts(const_map)
            if isinstance(sub, FormNum):
                num += sub
            else:
                terms.append(sub)
        if num == zero:
            return FormSum(terms)
        return FormSum(terms + [num])


class FormProd(_FormProdTemplate):
    def __init__(self, factors):
        # TODO functionality for products/large number of factors
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

    def match(self, expr, var_map):
        if isinstance(expr, Num):
            if self.isconst:
                return SingleConstraint(self, expr, var_map.copy())
            if expr == zero:
                # If expr is zero, still can be matched if any of the factors match with zero
                # since a zero in FormProd will make the whole thing zero
                consts = [f for f in self.factors if f.isconst]
                if not consts:
                    return False
                return FormProd(consts).match(zero, var_map.copy())
            return False
        if isinstance(expr, Prod) and len(self.factors) != len(expr.factors):
            if len(expr.factors) > len(self.factors):
                return False
            # Padding by *1
            ones = [one] * (len(self.factors) - len(expr.factors))
            factors = expr.factors + ones
            return self.match(Prod(factors), var_map.copy())
        if not isinstance(expr, Prod):
            # Padding by *1
            ones = [one] * (len(self.factors)-1)
            return self.match(Prod([expr] + ones), var_map.copy())
        matches = MultiConstraint(len(self.factors))
        for i, ff in enumerate(self.factors):
            for j, ef in enumerate(expr.factors):
                matches[i, j] = ff.match(ef, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        for factor in self.factors:
            if not factor.isconst:
                return False
        return True

    def group_consts(self):
        """Groups all constants in this FormProd into a single FormProd"""
        factors = [factor.group_consts() for factor in self.factors]
        temp = FormProd(factors)
        if temp.isconst:
            return temp
        consts = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isconst:
                consts.append(factors.pop(i))
        if len(consts) == 1:
            factors.append(consts[0])
        elif len(consts) > 1:
            factors.append(FormProd(consts))
        return FormProd(factors)

    @cached_property
    def get_consts(self):
        return set.union(*[factor.get_consts for factor in self.factors])

    @cached_property
    def get_vars(self):
        return set.union(*[factor.get_vars for factor in self.factors])
    
    def substitute_consts(self, const_map):
        factors = []
        num = zero
        for factor in self.factors:
            sub = factor.substitute_consts(const_map)
            if isinstance(sub, FormNum):
                num += sub
            else:
                factors.append(sub)
        if num == zero:
            return FormProd(factors)
        return FormProd(factors + [num])


class FormFrac(_FormFracTemplate):
    def __init__(self, numer, denom):
        self.numer = FormNum(numer) if FormNum.isnum(numer) else numer
        self.denom = FormNum(denom) if FormNum.isnum(denom) else denom

    def match(self, expr, var_map):
        if isinstance(expr, Num):
            if expr == zero:
                return self.numer.match(zero, var_map.copy())
            if self.isconst:
                return SingleConstraint(self, expr, var_map.copy())
            return False
        if not isinstance(expr, Frac):
            return self.match(Frac(expr, one), var_map.copy())
        matches = MultiConstraint(2)
        matches[0, 0] = self.numer.match(expr.numer, var_map.copy())
        matches[1, 1] = self.denom.match(expr.denom, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        if not self.numer.isconst:
            return False
        if not self.denom.isconst:
            return False
        return True

    def group_consts(self):
        return FormFrac(self.numer.group_consts(), self.denom.group_consts())

    @cached_property
    def get_consts(self):
        return self.numer.get_consts | self.denom.get_consts

    @cached_property
    def get_vars(self):
        return self.numer.get_vars | self.denom.get_vars

    def substitute_consts(self, const_map):
        numer = self.numer.substitute_consts(const_map)
        denom = self.denom.substitute_consts(const_map)
        if isinstance(numer, FormNum) and isinstance(denom, FormNum):
            return numer / denom
        return FormFrac(numer, denom)


class FormExp(_FormExpTemplate):
    def __init__(self, base, power):
        self.base = FormNum(base) if FormNum.isnum(base) else base
        self.power = FormNum(power) if FormNum.isnum(power) else power

    def match(self, expr, var_map):
        if isinstance(expr, Num):
            if expr == zero or expr == one:
                b1 = self.base.match(one, var_map.copy())
                if expr == one and b1:
                    return b1
                b0 = self.base.match(zero, var_map.copy())
                p0 = self.power.match(zero, var_map.copy())
                if expr == zero and b0 and not p0:
                    return b0
            if self.isconst:
                return SingleConstraint(self, expr, var_map.copy())
            return False
        if not isinstance(expr, Exp):
            return self.match(Exp(expr, one), var_map.copy())
        matches = MultiConstraint(2)
        matches[0, 0] = self.base.match(expr.base, var_map.copy())
        matches[1, 1] = self.power.match(expr.power, var_map.copy())
        if matches.check_validity():
            return matches
        return False

    @cached_property
    def isconst(self):
        if not self.base.isconst:
            return False
        if not self.power.isconst:
            return False
        return True

    def group_consts(self):
        return FormExp(self.base.group_consts(), self.power.group_consts())

    @cached_property
    def get_consts(self):
        return self.base.get_consts | self.power.get_consts

    @cached_property
    def get_vars(self):
        return self.base.get_vars | self.power.get_vars

    def substitute_consts(self, const_map):
        base = self.base.substitute_consts(const_map)
        power = self.power.substitute_consts(const_map)
        if isinstance(base, FormNum) and isinstance(power, FormNum):
            return base ** power
        return FormExp(base, power)


class FormEqn(_FormEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    
    def match(self, expr, var_map):
        if not isinstance(expr, Eqn):
            return False
        matches = MultiConstraint(2)
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


def solve_constraints(constrs, n_consts, n_vars):
    constrs = list(constrs)
    # Constructing a merged var_map from all the var_maps from the SingleConstraints
    var_map = {}
    for constr in constrs:
        if constr.var_map is None:
            continue
        for form, var in constr.var_map.items():
            if form in var_map:
                if var_map[form] == var:
                    if isinstance(form, FormVar) and \
                        Counter(var_map.values())[var] != 1:
                        return False
                else:
                    return False
            elif isinstance(form, FormVar) and \
                Counter(var_map.values())[var] != 0:
                return False
            var_map[form] = var

    # Var map cannot be fully accurately reconstructed
    if len(var_map) != n_vars:
        return False

    # There are no constants to solve for
    if n_consts == 0:
        return {}, var_map

    # Solving const_map from all the SingleConstraint.exprs and SingleConstraint.forms
    const_map = {}
    n_passes = len(constrs) - len(const_map)
    i = 0
    while len(const_map) < n_consts and i < n_passes:
        # Getting all 'lone' constants
        for constr in constrs:
            if isinstance(constr.form, FormConst):
                if constr.form in const_map:
                    return False
                const_map[constr.form] = constr.value
        for j, constr in enumerate(constrs):
            # Substitute
            # Create new instance of SingleConstraint to prevent downstream SingleConstraints from getting modified
            if constr.form is None:
                continue
            constr = SingleConstraint(form=constr.form.substitute_consts(const_map),
                                          value=constr.value)
            # Simplify
            constr.simplify()
            constrs[j] = constr
        i += 1
    if len(const_map) == n_consts:
        return const_map, var_map
    return False


def match(form, expr):
    var_map = {}
    matches = form.match(expr, var_map)
    if not matches:
        return False
    matches = matches.get_constraints()
    if not matches:
        return False
    # Calculating number of constants to solve for
    n_consts = len(form.get_consts)
    n_vars = len(form.get_vars)
    for constr in matches:
        result = solve_constraints(constr, n_consts, n_vars)
        if result:
            const_map, var_map = result
            return {'consts': const_map, 'vars': var_map}
    return False


if __name__ == '__main__':
    x = Var('x')
    y = FormVar('y')
    a = FormConst('a')
    b = FormConst('b')
    c = FormConst('c')
    d = FormConst('d')
    e = FormConst('e')
    # form = ((a*b+c)*y**3 + b*c*y**2 + c*d*y + d).group_consts()
    # expr =  10*x**3   + 12*x**2  + 20*x  + 5
    form = (y**(a*b+c) + b*c*y + b/y).group_consts()
    expr = (x**-5 + 2*x + 2/x)
    # form = y + 2
    # expr = x + 2

    # a1 = FormWild('a1')
    # a2 = FormWild('a2')
    # a3 = FormWild('a3')
    # form = a1**a2 * a2**a3
    # expr = x**2 * x**3

    # form = a*y**2+b*y+c
    # expr = 3*x**2-5*x-3
    # expr = expr.simplify()

    print(form)
    print(expr)
    print(match(form, expr))