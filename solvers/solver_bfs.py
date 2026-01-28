from itertools import product, compress, chain
import concurrent.futures
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
    eqns = {eqn}
    visited = set()
    while True:
        # SET POWER!!!!!!
        l = len(eqns)
        print(l)
        # eqns.update(*map(get_eqns, eqns))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for future in executor.map(get_eqns, eqns, chunksize=max(l//20,1)):
                eqns.update(future)
        eqns -= visited
        visited |= eqns
        for eqn in eqns:
            # print(eqn)
            match = match_any(eqn, forms)
            if match != -1:
                return match


def get_eqns(eqn):
    return solve_sum(eqn) + solve_prod(eqn)


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

def solve_prod(eqn):
    lhs, rhs = eqn.lhs, eqn.rhs
    eqns = []

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
        eqns.append(Eqn(*args))

    # Zero division check
    if lhs == zero or rhs == zero:
        return []

    # Shifting all factors to LHS
    factors = []
    factors.extend(lhs.decomp())
    temp_rhs = one / rhs
    factors.extend(temp_rhs.decomp())
    factors = [factor for factor in factors if factor != one]
    factors = Prod(factors).group().simplify().decomp()

    # Arranging factors on LHS and RHS in all combinations
    mask = product([False, True], repeat=len(factors)-1)
    lhs_mask = [(False,) + i for i in mask]
    rhs_mask = [[not i for i in mask] for mask in lhs_mask]
    lhss = [list(compress(factors, mask)) for mask in lhs_mask]
    rhss = [list(compress(factors, mask)) for mask in rhs_mask]
    for lhs, rhs in zip(lhss, rhss):
        new_lhs = Prod(lhs).simplify()
        new_rhs = (one / Prod(rhs)).simplify()
        if new_rhs == Undefined:
            continue
        eqns.append(Eqn(new_lhs, new_rhs))
    return eqns


if __name__ == '__main__':
    # eqn = Eqn((99*x+101)**2+101*x-x**2, 0)
    # print(solve(eqn))
    eqn = Eqn(1 / ((x + 1) ** 3), 1)
    print(solve(eqn))