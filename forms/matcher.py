from collections import Counter
from core.classes import *
from forms.classes import *
from forms.classes import SingleConstraint


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
                if constr.value not in constr.form.domain:
                    return False
                const_map[constr.form] = constr.value
        for j, constr in enumerate(constrs):
            # Substitute
            # Create new instance of SingleConstraint to prevent downstream SingleConstraints from getting modified,
            # since simplify runs in-place
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
    # form = (y**(a*b+c) + b*c*y + b/y).group_consts()
    # expr = (x**-5 + 2*x + 2/x)
    # form = y + 2
    # expr = x + 2

    a1 = FormWild('a1')
    a2 = FormWild('a2')
    a3 = FormWild('a3')
    # form = a1**a2 * a1**a3
    # expr = x**2 * x**3

    form = a1 + a2
    expr = x**2-x

    print(form)
    print(expr)
    print(match(form, expr))