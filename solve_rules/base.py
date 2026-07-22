from forms.classes import FORM_TYPES, FormEqn
import forms.matcher as matcher


__all__ = ['SolveRule', 'SolveGroup']


class SolveRule:
    def __init__(self, target_form, formula):
        if target_form is not None:
            if isinstance(target_form, FORM_TYPES) and not isinstance(target_form, FormEqn):
                self.target_form = FormEqn(target_form, 0).group_consts()
            else:
                self.target_form = target_form.group_consts()
            if isinstance(formula, FORM_TYPES):
                formula = (formula,)
            formula = tuple(formula)
            for formula_ in formula:
                if formula_.get_vars:
                    raise ValueError("'formulas' cannot contain FormVars")
            self.formula = tuple(formula)

    def apply(self, expr, first_result=True):
        result = matcher.match(self.target_form, expr)
        if not result:
            return None
        solns = []
        for formula in self.formula:
            soln = formula.substitute_consts(result['consts'])
            solns.append(soln.to_coretype(result['consts']).simplify())
        return solns


class SolveGroup:
    def __init__(self, rules):
        self.rules = rules

    def apply(self, expr, first_result=True):
        if first_result:
            for rule in self.rules:
                solns = rule.apply(expr, first_result)
                if solns:
                    return solns
            return []

        solns = []
        for rule in self.rules:
            solns.extend(rule.apply(expr, first_result))
        return solns