from collections import Counter, defaultdict
from functools import singledispatch, lru_cache

from .expr import *
from .pfactor import pfactor
from .utils import isrational # TODO to be replaced by intervals


__all__ = ['decomp', 'simplify', 'simplify_decomp']


def simplify_decomp(counter: Counter):
    new_decomp = Counter()
    for base, power in counter.items():
        new_decomp[base] = simplify(power)
    return new_decomp


def _exprize_decomp(counter: Counter):
    new_decomp = Counter()
    for base, power in counter.items():
        new_decomp[base] = make_expr(power)
    return new_decomp


##########
# DECOMP #
##########


@lru_cache
@singledispatch
def decomp(expr, top=True):
    pass


@decomp.register(Num)
def _(num, top=True):
    f = pfactor(num.value)
    if top:
        f = Counter({Num(base): Num(power) for base, power in f.items()})
    else:
        f = Counter({Num(base): power for base, power in f.items()})
    return f


@decomp.register(Var)
@decomp.register(Sum)
def _(var, top=True):
    if top:
        return Counter({var: one})
    return Counter({var: 1})


@decomp.register(Prod)
def _(prod, top=True):
    c = Counter()
    for factor in prod.factors:
        c.update(decomp(factor, top=False))
    c = simplify_decomp(c)
    if top:
        c = _exprize_decomp(c)
    return c


@decomp.register(Frac)
def _(frac, top=True):
    numers = decomp(frac.numer, top=False).copy()
    denoms = decomp(frac.denom, top=False)
    numers.subtract(denoms)
    numers = simplify_decomp(numers)
    if top:
        numers = _exprize_decomp(numers)
    return numers


@decomp.register(Exp)
def _(exp, top=True):
    if not exp.power.isnum:
        if top:
            return Counter({exp: one})
        return Counter({exp: 1})
    d = decomp(exp.base, top=False).copy()
    if isinstance(exp.power, Num):
        power = exp.power.value
    else:
        power = exp.power
    for expr in d:
        d[expr] = simplify(d[expr] * power)
    if top:
        d = _exprize_decomp(d)
    return d


# TODO how to decomp a Func?


@decomp.register(Eqn)
def _(eqn, top=True):
    raise TypeError("Cannot decomp an Eqn")


############
# SIMPLIFY #
############


@lru_cache
@singledispatch
def simplify(expr):
    pass


@simplify.register(int) # simplify sometimes processes int because decomp sometimes returns int
@simplify.register(Num)
@simplify.register(Var)
def _(expr):
    return expr


@simplify.register(Sum)
def _(sum):
    if len(sum.terms) == 1:
        return simplify(sum.terms[0])
    decomps = []
    for term in sum.terms:
        s = simplify(term)
        if s != 0:
            decomps.append(decomp(s))
    if sum.isnum:
        return _sum_no_vars(decomps)
    else:
        return _sum_with_vars(decomps)


@simplify.register(Prod)
def _(prod):
    if len(prod.factors) == 1:
        return simplify(prod.factors[0])
    d = decomp(Prod([simplify(factor) for factor in prod.factors]))
    numer = 1
    denom = 1
    factors = [] # non rational stuff
    for base, power in d.items():
        if isinstance(base, (Num, int)) and isinstance(power, (Num, int)):
            if power > 0:
                numer *= _get_int_value(base) ** _get_int_value(power)
            elif power < 0:
                denom *= _get_int_value(base) ** -_get_int_value(power)
        else:
            factors.append(simplify(Exp(base, power)))
    # DO NOT use Frac(numer, denom).simplify() as that uses Prod simplify,
    # which will cause RecursionError
    if numer == 0:
        return zero
    if denom == 0:
        raise ZeroDivisionError(f'{numer=}; {denom=}; {factors=}')

    if numer == 1 and denom != 1:
        const = Exp(denom, -1)
    elif numer != 1 and denom == 1:
        const = Num(numer)
    elif numer == 1 and denom == 1:
        const = one
    else:
        const = Prod([numer, Exp(denom, -1)])

    if len(factors) == 0:
        return const
    if const == 1 and len(factors) == 1:
        return factors[0]
    if const == 1 and len(factors) > 1:
        return Prod(factors)
    return const * Prod(factors)


@simplify.register(Frac)
def _(frac):
    numer = decomp(simplify(frac.numer)).copy()
    denom = decomp(simplify(frac.denom))
    numer.subtract(denom)
    numer = simplify_decomp(numer)
    s = simplify(decomp2prod(numer))
    return s


@simplify.register(Exp)
def _(exp):
    base = simplify(exp.base)
    power = simplify(exp.power)
    if isinstance(base, Exp):
        power = simplify(base.power * power)
        base = base.base
    if power == 1:
        return base
    if base == -1 and isinstance(power, Num):
        return Num(base.value ** power.value)
    if base == 1 or (power == 0 and base != 0):
        return one
    if base == 0 and power != 0:
        return zero
    if base == 0 and power == 0:
        return Exp(0, 0)
    if isinstance(base, Num):
        if isinstance(power, Num):
            if power > 0:
                # a^b where a and b are integers
                return Num(base.value ** power.value)
            if power < 0:
                return Exp(Num(base.value ** -power.value), -1)
        if isinstance(power, Exp) and isinstance(power.base, Num) and power.power == -1:
            # a^b where a is integer and b=1/int
            result = _pow_int_test(base, power)
            if result:
                return result
    return Exp(base, power)


@simplify.register(Func)
@simplify.register(Eqn)
def _(expr):
    return expr.apply(simplify)


def _sum_no_vars(decomps: list[Counter]):
    terms = defaultdict(list)
    # Extract rational and irrational numbers
    for d in decomps:
        expr = []
        coeff = []
        for base, power in d.items():
            temp = simplify(Exp(base, power))
            if isrational(temp):
                coeff.append(temp)
            else:
                expr.append(temp)
        terms[simplify(Prod(expr))].append(simplify(Prod(coeff)))
    output = []
    for expr, coeff in terms.items():
        # Sum rationals together
        coeff_simplify = _sum_fracs(coeff)
        term = _simplify_term(coeff_simplify, expr)
        output.append(term)
    if len(output) == 0:
        return 0
    if len(output) == 1:
        return output[0]
    return Sum(output)



def _sum_with_vars(decomps: list[Counter]):
    terms = defaultdict(list)
    # Extract variables and coefficients
    for d in decomps:
        expr = []
        coeff = []
        for base, power in d.items():
            temp = simplify(Exp(base, power))
            if temp.isnum:
                coeff.append(temp)
            else:
                expr.append(temp)
        terms[simplify(Prod(expr))].append(simplify(Prod(coeff)))
    output = []
    for expr, coeff in terms.items():
        # Simplify coefficients which will run via _sum_no_vars
        coeff_simplify = simplify(Sum(coeff))
        term = _simplify_term(coeff_simplify, expr)
        output.append(term)
    if len(output) == 0:
        return 0
    if len(output) == 1:
        return output[0]
    return Sum(output)


def _sum_fracs(coeffs: list):
    numers = []
    denoms = []
    int_ = 0
    for coeff in coeffs:
        if isinstance(coeff, Num):
            int_ += coeff.value
            continue
        n, d = _get_frac(coeff)
        numers.append(n)
        denoms.append(d)
    if len(numers) == 0:
        return Num(int_)
    numers.append(Num(int_))
    denoms.append(one)
    numer = 0
    denom = 1
    for i, n in enumerate(numers):
        numer_ = 1
        for j, d in enumerate(denoms):
            if i == j:
                numer_ *= n.value
                denom *= d.value
            else:
                numer_ *= d.value
        numer += numer_
    return simplify(Frac(numer, denom))


def _simplify_term(coeff, expr):
    if coeff == 0 or expr  == 0:
        return zero
    if coeff == 1 and expr == 1:
        return one
    if coeff == 1:
        return expr
    if expr == 1:
        return coeff
    return simplify(coeff * expr)


def _get_frac(expr):
    if isinstance(expr, Prod):
        if isinstance(expr.factors[0], Exp):
            return (expr.factors[1], expr.factors[0].base)
        return (expr.factors[0], expr.factors[1].base)
    if isinstance(expr, Exp):
        return (one, expr.base)
    raise ValueError(f"Cannot turn expr into fraction: {expr}")


def _get_int_value(num):
    if isinstance(num, Num):
        return num.value
    return num


def _pow_int_test(base: Num, power: Exp):
    f = pfactor(base.value)
    f_new = {}
    for p, n in f.items():
        if n % power.base.value != 0:
            return None
        f_new.update({p: n // power.base.value})
    result = 1
    for p, n in f_new.items():
        result *= p ** n
    return Num(result)


if __name__ == '__main__':
    x = Var('x')
    y = Var('y')
    print(decomp(x * y * x ** 3 * y ** -3))
    # sqrt2 = Exp(2, Exp(2, -1))
    # print(simplify(2 * sqrt2))