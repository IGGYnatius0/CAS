from core.core_classes import *
from forms.form_classes import *


__all__ = ['RewriteRule', 'RewriteSet', 'RewriteGroup']


def substitute(form, const_map, var_map):
    if isinstance(form, FormConst):
        return sub_const(form, const_map, var_map)
    if isinstance(form, FormVar):
        return sub_var(form, const_map, var_map)
    if isinstance(form, FormExpr):
        return sub_expr(form, const_map, var_map)
    if isinstance(form, FormSum):
        return sub_sum(form, const_map, var_map)
    if isinstance(form, FormProd):
        return sub_prod(form, const_map, var_map)
    if isinstance(form, FormFrac):
        return sub_frac(form, const_map, var_map)
    if isinstance(form, FormExp):
        return sub_exp(form, const_map, var_map)
    return form


def sub_const(form: FormConst, const_map: dict, var_map: dict):
    if form in const_map:
        return const_map[form]
    return form


def sub_var(form: FormVar, const_map: dict, var_map: dict):
    if form in var_map:
        return var_map[form]
    return form


def sub_expr(form: FormExpr, const_map: dict, var_map: dict):
    if form in var_map:
        return var_map[form]
    return form


def sub_sum(form: FormSum, const_map: dict, var_map: dict):
    return Sum([substitute(term, const_map, var_map) for term in form.terms])


def sub_prod(form: FormProd, const_map: dict, var_map: dict):
    return Prod([substitute(factor, const_map, var_map) for factor in form.factors])


def sub_frac(form: FormFrac, const_map: dict, var_map: dict):
    return Frac(substitute(form.numer, const_map, var_map),
                substitute(form.denom, const_map, var_map))


def sub_exp(form: FormExp, const_map: dict, var_map: dict):
    return Exp(substitute(form.base, const_map, var_map),
               substitute(form.power, const_map, var_map))


class RewriteRule:
    def __init__(self, form, target):
        self.form = form
        self.target = target

    def rewrite(self, expr, simplify=True):
        result = match(self.form, expr)
        if result:
            const_map, var_map = result['consts'], result['vars']
            new = substitute(self.target, const_map, var_map)
            if simplify:
                new = new.simplify()
            if new == expr: # Dont return the same thing
                return []
            return [new]
        else:
            return []


class RewriteSet:
    def __init__(self, forms):
        self.forms = forms

    def rewrite(self, expr, simplify=True):
        # TODO change to generator?
        # Finding which form exr matches, if any
        for i, form in enumerate(self.forms):
            result = match(form, expr)
            if result:
                const_map, var_map = result['consts'], result['vars']
                idx = i
                break
        else:
            return []
        # Transform to the rest of the forms
        new = []
        for i, form in enumerate(self.forms):
            if i == idx:
                continue
            temp = substitute(form, const_map, var_map)
            if simplify:
                temp = temp.simplify()
            if temp != expr: # Dont return the same thing
                new.append(temp)
        return list(set(new))


class RewriteGroup:
    def __init__(self, rules):
        self.rules = rules

    def rewrite(self, expr, simplify=True):
        new = []
        for rule in self.rules:
            new.extend(rule.rewrite(expr, simplify))
        return list(set(new))