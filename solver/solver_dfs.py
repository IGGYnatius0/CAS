from itertools import product, compress

from core.core_classes import *
from core.core_classes import neg_one, one
from core.abc import x
from forms.known_forms import forms

# FIXME NOT WORKING YET!!!

def match_any(eqn, _forms):
    for i, form in enumerate(_forms):
        if form.match(eqn):
            print(eqn)
            return i
    return -1

visited = []

def solve(eqn, target, mode=0):
    global visited
    if eqn in visited or eqn.swap() in visited:
        return -1
    if eqn.isequal():
        return -2
    print(eqn)
    match = match_any(eqn, forms)
    if match != -1:
        return match
    visited.append(eqn)
    sum_res = solve_sum(eqn, target)
    if sum_res != -1:
        return sum_res
    return solve_prod(eqn, target)


def solve_sum(eqn, target):
    lhs, rhs = eqn.lhs, eqn.rhs

    # Solving factorised cases
    if isinstance(lhs, Sum):
        lhsf = lhs.factorise().simplify()
    else:
        lhsf = lhs
    if isinstance(rhs, Sum):
        rhsf = rhs.factorise().simplify()
    else:
        rhsf = rhs
    for args in [(lhsf, rhsf), (lhsf, rhs), (lhs, rhsf)]:
        s = solve(Eqn(*args), target)
        if s != -1:
            return s

    # Shifting all terms to LHS
    terms = []
    if isinstance(lhs, Sum):
        terms.extend(lhs.terms)
    else:
        terms.append(lhs)
    temp_rhs = neg_one * rhs
    if Num.isnum(temp_rhs):
        terms.append(temp_rhs)
    else:
        temp_rhs = temp_rhs.expand()
        if isinstance(temp_rhs, Sum):
            terms.extend(temp_rhs.terms)
        else:
            terms.append(temp_rhs)
    terms = [term for term in terms if term != zero]

    # Arranging terms on LHS and RHS in all combinations
    mask = product([False,True], repeat=len(terms)-1)
    lhs_mask = [(False,) + i for i in mask]
    rhs_mask = [[not i for i in mask] for mask in lhs_mask]
    lhss = [list(compress(terms, mask)) for mask in lhs_mask]
    rhss = [list(compress(terms, mask)) for mask in rhs_mask]
    for lhs, rhs in zip(lhss, rhss):
        new_lhs = Sum(lhs).simplify()
        new_rhs = (neg_one * Sum(rhs)).expand().simplify()
        new_eqn = Eqn(new_lhs, new_rhs)
        s = solve(new_eqn, target)
        if s != -1:
            return s
    return -1

def solve_prod(eqn, target):
    lhs, rhs = eqn.lhs, eqn.rhs

    # Solving expanded cases
    if isinstance(lhs, Prod):
        lhse = lhs.expand().simplify()
    else:
        lhse = lhs
    if isinstance(rhs, Prod):
        rhse = rhs.expand().simplify()
    else:
        rhse = rhs
    for args in [(lhse, rhse), (lhse, rhs), (lhs, rhse)]:
        s = solve(Eqn(*args), target)
        if s != -1:
            return s

    # Zero division check
    if lhs == zero or rhs == zero:
        return -1

    # Shifting all factors to LHS
    factors = []
    factors.extend(lhs.decomp())
    temp_rhs = one / rhs
    factors.extend(temp_rhs.decomp())
    factors = [factor for factor in factors if factor != one]

    # Arranging factors on LHS and RHS in all combinations
    mask = product([False, True], repeat=len(factors)-1)
    lhs_mask = [(False,) + i for i in mask]
    rhs_mask = [[not i for i in mask] for mask in lhs_mask]
    lhss = [list(compress(factors, mask)) for mask in lhs_mask]
    rhss = [list(compress(factors, mask)) for mask in rhs_mask]
    for lhs, rhs in zip(lhss, rhss):
        new_lhs = Prod(lhs).simplify()
        new_rhs = (one / Prod(rhs)).simplify()
        new_eqn = Eqn(new_lhs, new_rhs)
        s = solve(new_eqn, target)
        if s != -1:
            return s
    return -1


if __name__ == '__main__':
    eqn = Eqn(1/((x+1)**3), 1)
    print(solve(eqn, x))
