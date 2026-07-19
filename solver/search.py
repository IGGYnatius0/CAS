from functools import lru_cache
from forms.known_forms import FORMS
from forms.formulas import FORMULAS
import forms.matcher as matcher
from solver.rewrite import rewrite


def match_form(expr):
    for i, form in enumerate(FORMS):
        match_result = matcher.match(expr, form)
        if match_result:
            return i, match_result
    return None


def iterative_deepening_inner(eqn, max_depth, current_depth):
    new_eqns = rewrite(eqn)
    for new_eqn in new_eqns:
        iterative_deepening_inner(new_eqn, max_depth, current_depth + 1)