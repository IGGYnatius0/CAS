from itertools import product, chain

from .registry import FORMS
from CAS.core.expr import *


class SingleConstraint:
    def __init__(self, form=None, value=None, var_map=None):
        self.form = form
        self.value = value
        self.var_map = var_map

    def get_constraints(self):
        """Returns a generator of all possible combinations of constraints"""
        yield (self,)
        return

    def simplify(self):
        prev_form = None
        while self.form != prev_form:
            prev_form = self.form
            if isinstance(self.form, FORMS.sum):
                self.simplify_sum()
            elif isinstance(self.form, FORMS.prod):
                self.simplify_prod()
            elif isinstance(self.form, FORMS.frac):
                self.simplify_frac()
            elif isinstance(self.form, FORMS.exp):
                self.simplify_exp()
            if isinstance(self.form, FORMS.sum) and len(self.form.terms) == 1:
                self.form = self.form.terms[0]
            elif isinstance(self.form, FORMS.prod) and len(self.form.factors) == 1:
                self.form = self.form.factors[0]

    def simplify_sum(self):
        for i, term in enumerate(self.form.terms):
            if isinstance(term, FORMS.num):
                self.value -= term.value
                self.form.terms.pop(i)
                return

    def simplify_prod(self):
        for i, factor in enumerate(self.form.factors):
            if isinstance(factor, FORMS.num):
                self.value /= factor.value # FIXME possible division by zero
                self.form.factors.pop(i)
                return

    def simplify_frac(self):
        if isinstance(self.form.numer, FORMS.num):
            self.value = self.form.numer.value / self.value
            self.form = self.form.denom
        elif isinstance(self.form.denom, FORMS.num):
            self.value *= self.form.denom.value
            self.form = self.form.numer

    def simplify_exp(self):
        if isinstance(self.form.base, FORMS.num):
            # TODO logarithm
            pass
        elif isinstance(self.form.power, FORMS.num):
            self.value **= one / self.form.power.value
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
            if not constr or (isinstance(constr, SingleConstraint) and constr.form is None):
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


FORMS.SingleConstraint = SingleConstraint
FORMS.MultiConstraint = MultiConstraint