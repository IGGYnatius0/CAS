from decimal import Decimal
from itertools import product, chain

from core.core_classes import *
from core.num import *

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


class _FormEqnTemplate:
    def __eq__(self, other):
        if not isinstance(other, _FormEqnTemplate):
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


class SingleConstraint:
    def __init__(self, form=None, value=None, var_map=None):
        self.form = form
        self.value = value
        self.var_map = var_map

    def sort_matches(self):
        """Sorts self.matches by increasing number of constraints"""
        return [[self]]

    def get_constraints(self):
        """Returns a generator of all possible combinations of constraints"""
        return [[self]]

    def solve(self):
        prev_form = None
        while self.form != prev_form:
            if isinstance(self.form, FormSum):
                self.solve_sum()
            if isinstance(self.form, FormProd):
                self.solve_prod()
            if isinstance(self.form, FormFrac):
                self.solve_frac()
            if isinstance(self.form, FormExp):
                self.solve_exp()
            prev_form = self.form
        if isinstance(self.form, FormSum) and len(self.form.terms) == 1:
            self.form = self.form.terms[0]
        if isinstance(self.form, FormProd) and len(self.form.factors) == 1:
            self.form = self.form.factors[0]
        # if isinstance(self.form, FormFrac):
        #     pass
        # if isinstance(self.form, FormExp):
        #     pass

    def solve_sum(self):
        for i, term in enumerate(self.form.terms):
            if isinstance(term, Decimal):
                self.value -= Num(term)
                self.form.terms.pop(i)
                return

    def solve_prod(self):
        for i, factor in enumerate(self.form.factors):
            if isinstance(factor, Decimal):
                self.value /= Num(factor)
                self.form.factors.pop(i)
                return

    def solve_frac(self):
        if isinstance(self.form.numer, Decimal):
            self.value = Num(self.form.numer) / self.value
            self.form = self.form.denom
        elif isinstance(self.form.denom, Decimal):
            self.value *= Num(self.form.denom)
            self.form = self.form.numer

    def solve_exp(self):
        if isinstance(self.form.base, Decimal):
            # TODO logarithm
            pass
        elif isinstance(self.form.power, Decimal):
            self.value **= 1 / Num(self.form.power)
            self.form = self.form.base

    def __bool__(self):
        return True

    def __repr__(self):
        return f'({str(self.form)}: {str(self.value)})'

    def __str__(self):
        return f'({str(self.form)}: {str(self.value)})'


class MultiConstraint:
    def __init__(self, fsize, esize):
        self.matches = [[False] * esize for _ in range(fsize)]
        self.nmatches = [0] * fsize

    def check_validity(self):
        """Checks if every row and column of self.matches has at least 1 constraint"""
        for form_match in self.matches:
            if not any(form_match):
                return False
        for i in range(len(self.matches[0])):
            if not any(value_match[i] for value_match in self.matches):
                return False
        return True

    def sort_matches(self):
        """Sorts self.matches by increasing number of constraints"""
        for form_matches in self.matches:
            for match in form_matches:
                if match:
                    match.sort_matches()
        sorted_matches = sorted(zip(self.nmatches, self.matches), key=lambda x: x[0]) # TODO confirm if need to reverse
        self.matches = [match[1] for match in sorted_matches]
        return self.matches

    def get_constraints(self):
        """Returns a generator of all possible combinations of constraints"""
        matches = []
        for form_matches in self.matches:
            temp = []
            for match in form_matches:
                if isinstance(match, MultiConstraint) or (isinstance(match, SingleConstraint) and match.form is not None):
                    temp.extend(chain(*match.get_constraints()))
            if len(temp) > 0:
                matches.append(temp)
        return product(*matches)

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

    def match(self, expr, var_map={}):
        if expr == self:
            return SingleConstraint(var_map=var_map)
        return False

    def isconst(self):
        return True

    def group_consts(self):
        return self

    def get_consts(self):
        return set()

    def substitute(self, const_map):
        return self

    @classmethod
    def isnum(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"FormNum({str(self)})"

    def __hash__(self):
        return hash(('FormNum', super().__hash__()))


class FormConst(_FormConstTemplate):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map={}):
        if not isinstance(expr, Num):
            return False
        return SingleConstraint(self, expr, var_map)

    def isconst(self):
        return True

    def group_consts(self):
        return self

    def get_consts(self):
        return {self}

    def substitute(self, const_map):
        if self in const_map:
            return FormNum(const_map[self])
        return self


class FormVar(_FormVarTemplate):
    def __init__(self, sym):
        self.sym = sym

    def match(self, expr, var_map={}):
        if not isinstance(expr, Var):
            return False
        if expr in var_map:
            match = var_map[expr] == self
            if match:
                return SingleConstraint(self, expr, var_map=var_map)
            return False
        var_map[expr] = self
        return SingleConstraint(var_map=var_map)

    def isconst(self):
        return False

    def group_consts(self):
        return self

    def get_consts(self):
        return set()
    
    def substitute(self, const_map):
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

    def match(self, expr, var_map={}):
        if isinstance(expr, Num):
            if self.isconst():
                return SingleConstraint(self, expr, var_map)
            return False
        if not isinstance(expr, Sum):
            return self.match(Sum([expr, Num(0)]))
        matches = MultiConstraint(len(self.terms), len(expr.terms))
        for i, ft in enumerate(self.terms):
            for j, et in enumerate(expr.terms):
                match = ft.match(et, var_map)
                if match:
                    matches[i, j] = match
        if matches.check_validity():
            return matches
        return False

    def isconst(self):
        for term in self.terms:
            if not term.isconst():
                return False
        return True

    def group_consts(self):
        """Groups all constants in this FormSum into a single FormSum"""
        terms = [term.group_consts() for term in self.terms]
        temp = FormSum(terms)
        if temp.isconst():
            return temp
        consts = []
        for i, term in reversed(list(enumerate(terms))):
            if term.isconst():
                consts.append(terms.pop(i))
        if len(consts) == 1:
            terms.append(consts[0])
        elif len(consts) > 1:
            terms.append(FormSum(consts))
        return FormSum(terms)

    def get_consts(self):
        return set.union(*[term.get_consts() for term in self.terms])
    
    def substitute(self, const_map):
        terms = []
        num = zero
        for term in self.terms:
            sub = term.substitute(const_map)
            if isinstance(sub, FormNum):
                num += sub
            else:
                terms.append(sub)
        if num == zero:
            return FormSum(terms)
        return FormSum(terms + [num])


class FormProd(_FormProdTemplate):
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
        if isinstance(expr, Num):
            if self.isconst():
                return SingleConstraint(self, expr, var_map)
            return False
        if not isinstance(expr, Prod):
            return self.match(Prod([expr, Num(1)]))
        matches = MultiConstraint(len(self.factors), len(expr.factors))
        for i, ff in enumerate(self.factors):
            for j, ef in enumerate(expr.factors):
                matches[i, j] = ff.match(ef, var_map)
        if matches.check_validity():
            return matches
        return False

    def isconst(self):
        for factor in self.factors:
            if not factor.isconst():
                return False
        return True

    def group_consts(self):
        """Groups all constants in this FormProd into a single FormProd"""
        factors = [factor.group_consts() for factor in self.factors]
        temp = FormProd(factors)
        if temp.isconst():
            return temp
        consts = []
        for i, factor in reversed(list(enumerate(factors))):
            if factor.isconst():
                consts.append(factors.pop(i))
        if len(consts) == 1:
            factors.append(consts[0])
        elif len(consts) > 1:
            factors.append(FormProd(consts))
        return FormProd(factors)

    def get_consts(self):
        return set.union(*[factor.get_consts() for factor in self.factors])
    
    def substitute(self, const_map):
        factors = []
        num = zero
        for factor in self.factors:
            sub = factor.substitute(const_map)
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

    def match(self, expr, var_map={}):
        # TODO guard clauses for 0 and 1 case
        if isinstance(expr, Num):
            if self.isconst():
                return SingleConstraint(self, expr, var_map)
            return False
        if not isinstance(expr, Frac):
            return False
        matches = MultiConstraint(2, 2)
        matches[0, 0] = self.numer.match(expr.numer)
        matches[0, 1] = self.numer.match(expr.denom)
        matches[1, 0] = self.denom.match(expr.numer)
        matches[1, 1] = self.denom.match(expr.denom)
        return matches
        # # Non-Frac case
        # if not isinstance(expr, Frac):
        #     return self.match(expr / one, var_map)
        # # Others
        # if not self.numer.match(expr.numer, var_map):
        #     return False
        # if not self.denom.match(expr.denom, var_map):
        #     return False
        # return True

    def isconst(self):
        if not self.numer.isconst():
            return False
        if not self.denom.isconst():
            return False
        return True

    def group_consts(self):
        return FormFrac(self.numer.group_consts(), self.denom.group_consts())

    def get_consts(self):
        return self.numer.get_consts() | self.denom.get_consts()

    def substitute(self, const_map):
        numer = self.numer.substitute(const_map)
        denom = self.denom.substitute(const_map)
        if isinstance(numer, FormNum) and isinstance(denom, FormNum):
            return numer / denom
        return FormFrac(numer, denom)


class FormExp(_FormExpTemplate):
    def __init__(self, base, power):
        self.base = FormNum(base) if FormNum.isnum(base) else base
        self.power = FormNum(power) if FormNum.isnum(power) else power

    def match(self, expr, var_map={}):
        # TODO guard clauses for 0 and 1 case
        if isinstance(expr, Num):
            if self.isconst():
                return SingleConstraint(self, expr, var_map)
            return False
        if not isinstance(expr, Exp):
            return False
        matches = MultiConstraint(2, 2)
        matches[0, 0] = self.base.match(expr.base)
        matches[0, 1] = self.base.match(expr.power)
        matches[1, 0] = self.power.match(expr.base)
        matches[1, 1] = self.power.match(expr.power)
        return matches

    def isconst(self):
        if not self.base.isconst():
            return False
        if not self.power.isconst():
            return False
        return True

    def group_consts(self):
        return FormExp(self.base.group_consts(), self.power.group_consts())

    def get_consts(self):
        return self.base.get_consts() | self.power.get_consts()

    def substitute(self, const_map):
        base = self.base.substitute(const_map)
        power = self.power.substitute(const_map)
        if isinstance(base, FormNum) and isinstance(power, FormNum):
            return base ** power
        return FormExp(base, power)


class FormEqn(_FormEqnTemplate):
    def __init__(self, lhs, rhs):
        self.lhs = FormNum(lhs) if FormNum.isnum(lhs) else lhs
        self.rhs = FormNum(rhs) if FormNum.isnum(rhs) else rhs

    # def match(self, value, var_map={}):
    #     if not isinstance(value, Eqn):
    #         return False
    #     return ((self.lhs.match(value.lhs, var_map) and self.rhs.match(value.rhs, var_map)) or
    #             (self.lhs.match(value.rhs, var_map) and self.rhs.match(value.lhs, var_map)))


def solve_constraints(constrs):
    const_map = {}
    # 1st pass: getting number of constants to solve for
    consts = set.union(*[constr.form.get_consts() for constr in constrs])
    n = len(consts)
    constrs = list(constrs)
    n_passes = len(constrs) - len(const_map)
    i = 0
    while len(const_map) < n and i < n_passes:
        # Getting all 'lone' constants
        for constr in constrs:
            form = constr.form
            if isinstance(form, FormConst):
                if form in const_map:
                    return False
                const_map[form] = constr.value
        # Substitute
        pass
        for j, constr in enumerate(constrs):
            constrs[j].form = constr.form.substitute(const_map)
        # Simplify
        pass
        for j, constr in enumerate(constrs):
            constr.solve()
        pass
        i += 1
    return const_map


def match(form, expr):
    matches = form.match(expr)
    matches.sort_matches()
    matches = matches.get_constraints()
    # for i in matches:
    #     print(list(i))
    for constr in matches:
        print(solve_constraints(constr))



if __name__ == '__main__':
    x = Var('x')
    y = FormVar('y')
    a = FormConst('a')
    b = FormConst('b')
    c = FormConst('c')
    d = FormConst('d')
    e = FormConst('e')
    # form = (a*b*y**3 + b*c*y**2 + c*d + d*y).group_consts()
    # expr =  6*x**3   + 12*x**2  + 20  + 5*x
    form = (a*y**2 + b*c*y + c).group_consts()
    expr = 2*x**2 + 12*x + 4
    print(form)
    print(expr)
    # TODO not fully working
    match(form, expr)
