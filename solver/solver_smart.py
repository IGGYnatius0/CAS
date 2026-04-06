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


def solve(eqn):
    new_eqn = convert(eqn)
    return _solve(new_eqn)


def convert(eqn):
    lhs = eqn.lhs
    rhs = eqn.rhs
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
    terms = Sum(terms).group().simplify()
    to_mul = []
    for term in terms.terms:
        if isinstance(term, Prod):
            denom = term.to_frac().denom
            to_mul.extend(denom.decomp())
    to_mul = Prod(to_mul)
    new_lhs = (to_mul * terms).expand().simplify()
    return Eqn(new_lhs, zero)


def _solve(eqn):
    eqns = {eqn}
    visited = set()
    while True:
        # SET POWER!!!!!!
        l = len(eqns)
        eqns.update(*map(solve_sum, eqns))
        eqns -= visited
        visited |= eqns
        for eqn in eqns:
            print(eqn)
            match = match_any(eqn, forms)
            if match != -1:
                return match


def solve_sum(eqn):
    lhs, rhs = eqn.lhs, eqn.rhs
    eqns = []

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
        eqns.append(Eqn(*args))

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
    sum = Sum(terms).group().simplify()
    if isinstance(sum, Sum):
        terms = sum.terms
    else:
        terms = [sum]

    # Arranging terms on LHS and RHS in all combinations
    mask = product([False,True], repeat=len(terms)-1)
    lhs_mask = [(False,) + i for i in mask]
    rhs_mask = [[not i for i in mask] for mask in lhs_mask]
    lhss = [list(compress(terms, mask)) for mask in lhs_mask]
    rhss = [list(compress(terms, mask)) for mask in rhs_mask]
    for lhs, rhs in zip(lhss, rhss):
        new_lhs = Sum(lhs).simplify()
        new_rhs = (neg_one * Sum(rhs)).expand().simplify()
        eqns.append( Eqn(new_lhs, new_rhs))
    return eqns


if __name__ == '__main__':
    eqn = Eqn((x**3-x)/x+(x**2+2*x-3)**2, (x**2+2*x+1)+(x**2-x-2))
    # eqn = Eqn((3*x+1)**2, 4*x-5)
    print(solve(eqn))
    pass