from core.core_classes import *

def diff_sum(expr):
    return Sum([diff(term) for term in expr.terms])


def diff_prod(expr):
    # Removing constants for efficiency
    factors = expr.factors
    const = one
    for i, factor in list(enumerate(factors))[::-1]:
        if isinstance(factor, Num):
            const *= factor
            factors.pop(i)

    terms = []
    for i, factor in enumerate(factors):
        factors_ = [diff(expr.factors[i])]
        for j, factor_ in enumerate(factors):
            if j != i:
                factors_.append(factor_)
        terms.append(Prod(factors_))
    if const == one:
        return Sum(terms)
    return const * Sum(terms)


def diff_frac(expr):
    return (expr.denom * diff(expr.numer) - expr.numer * diff(expr.denom)) / (expr.denom ** 2)


def diff_var(expr):
    return one


def diff_num(expr):
    return zero


def diff(expr):
    # TODO functions are not implemented in core_classes
    if isinstance(expr.base, Num) and not isinstance(expr.power, Num):
        return log(expr.base) * diff(expr.power) * expr
    if not isinstance(expr.base, Num) and isinstance(expr.power, Num):
        return expr.power * diff(expr.base) * expr.base ** (expr.power-1)
    return expr.base ** (expr.power-1) * \
        (expr.power*diff(expr.base) + expr.base*log(expr.base)*diff(expr.power))


if __name__ == "__main__":
    pass