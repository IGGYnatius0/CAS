import heapq
from collections import Counter
from functools import cached_property
from itertools import groupby

from core.classes import *
from core.abc import a, b, c, x


__all__ = ['groebner_basis']

# TODO add more types of ordering lex, grlex, grevlex, degrevlex
def lex_sort(terms, ordering):
    # Split into buckets by leading variable
    new_terms = {var: [] for var in ordering}
    no_var = []
    for term in terms:
        for var in ordering:
            if var in term:
                new_terms[var].append(term)
                break
        else:
            no_var.append(term)
    lexsorted = []
    for i, (var, terms_) in enumerate(new_terms.items()):
        # Sort by decreasing power
        terms_.sort(key=lambda x: x[var], reverse=True)
        # Split into buckets by power
        groupby_power = groupby(terms_, key=lambda x: x[var])
        for power, terms__ in groupby_power:
            terms__ = tuple(terms__)
            # ^ DO NOT DELETE because terms__ is used multiple times, and being a generator
            # (because itertools functions produce generators) it will get exhausted and the second time
            # terms__ is used it will return nothing
            # Base case
            if i+1 == len(ordering):
                lexsorted.extend(terms__)
                continue
            # Removing highest ranking variable
            for term in terms__:
                term.pop(var)
            # Recursive
            temp = lex_sort(terms__, ordering[i + 1:])
            # Add back variable
            for term in temp:
                term.update({var: power})
            lexsorted.extend(temp)
    return lexsorted + no_var


def lex_cmp(term1: Counter, term2: Counter, ordering) -> bool:
    """Returns term1 > term2 by lex ordering rules"""
    for var in ordering:
        if var in term1 and var not in term2:
            return True
        if var not in term1 and var not in term2:
            continue
        if term1[var] > term2[var]:
            return True
        if term1[var] < term2[var]:
            return False
    return False


class MultiVariatePolynomial(Sum):
    def __init__(self, expr: CORE_EXPR | list, ordering):
        if isinstance(expr, list):
            expr = Sum(expr)
        if set(ordering) < expr.get_vars:
            raise ValueError('`ordering` must contain all variables in `expr`')
        if isinstance(expr, Sum):
            terms = expr.terms
        else:
            terms = [expr]

        decomp = []
        num = None
        for term in terms:
            if isinstance(term, Num):
                num = term
            else:
                decomp.append(term.decomp())
        terms = lex_sort(decomp, ordering)
        terms = [decomp2prod(term).simplify() for term in terms]
        if num is not None:
            terms.append(num)
        super().__init__(terms)
        self.ordering = ordering

    @cached_property
    def LT(self) -> Counter:
        return self.terms[0].decomp()

    @cached_property
    def LM(self) -> Counter:
        return Counter({base: power for base, power in self.LT.items() if isinstance(base, Var)})

    @cached_property
    def LC(self) -> Counter:
        return Counter({base: power for base, power in self.LT.items() if isinstance(base, Num)})

    def copy(self):
        return MultiVariatePolynomial(super().copy(), self.ordering)


MVP = MultiVariatePolynomial


def s_poly(p: MVP, q: MVP):
    temp = decomp2prod(p.LM | q.LM) * (p / decomp2prod(p.LT) - q / decomp2prod(q.LT))
    temp = temp.simplify().expand().simplify()
    return MVP(temp, p.ordering)


def reduce(expr: MVP, polys):
    expr = expr.copy()
    q = [[] for _ in range(len(polys))]
    r = []
    while expr.terms != [zero]:
        for i, poly in enumerate(polys):
            if not poly.LM <= expr.LM:
            # if lex_cmp(poly.LM, expr.LM, expr.ordering):
                continue
            # Multiply divisor by appropriate amount and subtract result from original polynomial
            mul = expr.LT.copy()
            mul.subtract(poly.LT)
            q[i].append(mul)
            new_poly = (poly * decomp2prod(mul)).expand().simplify()
            ordering = expr.ordering
            expr = (expr - new_poly).expand().simplify()
            expr = MVP(expr, ordering)
            break
        else:
            # Transfer to remainder
            r.append(decomp2prod(expr.LT))
            expr = MVP(expr.terms[1:], expr.ordering)
    return Sum(r).simplify()


def product_criterion(f, g):
    return not bool(f.LM & g.LM)


def chain_criterion(G, i, j, reduced):
    # Compute LCM
    lcm = G[i].LM | G[j].LM
    for k in range(i): # i always < j
        if G[k].LM <= lcm:
            if k > i:
                a, b = i, k
            else:
                a, b = k, i
            if (a, b) not in reduced:
                continue
            if k > j:
                a, b = j, k
            else:
                a, b = k, j
            if (a, b) not in reduced:
                continue
            return True
    return False


def lcm_size(f: MVP, g: MVP) -> int:
    return sum((f.LM | g.LT).values())


def buchberger(F, ordering):
    reduced = []
    G = F.copy()

    pairs = []
    for i in range(len(G)):
        for j in range(i+1, len(G)):
            if i > j:
                i, j = j, i
            pairs.append((lcm_size(G[i], G[j]), i, j))
    heapq.heapify(pairs)

    while pairs:
        _, i, j = heapq.heappop(pairs)

        if product_criterion(G[i], G[j]) or chain_criterion(G, i, j, reduced):
            reduced.append((i, j))
            continue

        s = s_poly(G[i], G[j])
        r = reduce(s, G)
        if r != zero:
            r = MVP(r, ordering)
            pairs.extend([(lcm_size(k_poly, r), k, len(G)) for k, k_poly in enumerate(G)])
            heapq.heapify(pairs)
            G.append(r)
        else:
            reduced.append((i, j))
    return G


def reduced_gb(G, ordering):
    # Converting leading coefficient to 1
    for i, poly in enumerate(G):
        G[i] = MVP((poly * (1/decomp2prod(poly.LC))).expand().simplify(), ordering)
    # Minimise
    idxs = list(range(len(G)))
    for i, poly in enumerate(G):
        if i not in idxs:
            continue
        delete = []
        for j in idxs:
            if j == i:
                continue
            if poly.LT <= G[j].LT:
                delete.append(j)
        for j in delete:
            idxs.remove(j)
    G_min = [G[i] for i in idxs]
    # Inter-reduction
    G_red = []
    for i, poly in enumerate(G_min):
        polys = [poly_ for j, poly_ in enumerate(G_min) if j != i]
        G_red.append(MVP(reduce(poly, polys), ordering))
    return G_red


def groebner_basis(polys, ordering):
    mvps = []
    for poly in polys:
        if not isinstance(poly, MVP):
            mvps.append(MVP(poly, ordering))
        else:
            mvps.append(poly)
    gb = buchberger(mvps, ordering)
    reduced = reduced_gb(gb, ordering)
    return reduced


if __name__ == '__main__':
    ordering = [a, b, x]
    polys = [a+b-x**2+2*x-1,
             a**3-x**2,
             b**2-x]

    # ordering = [x, y]
    # polys = [x**2+y**2-2,
    #          x*y-1]

    polys = [MVP(poly, ordering) for poly in polys]
    b = groebner_basis(polys, ordering)
    for i in b:
        print(i)