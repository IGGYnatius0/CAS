from math import sqrt as msqrt
from math import ceil
from operator import mul
from functools import reduce, cache
from decimal import Decimal

primes = [2, 3, 5]

_neg1 = Decimal(-1)
_0 = Decimal(0)
_1 = Decimal(1)

def sqrt(x):
    return x ** 0.5


def prod(iterable):
    return reduce(mul, iterable, 1)


@cache
def isprime(x):
    for n in range(2, ceil(msqrt(x))):
        if not x % n:
            return False
    return True


def cache_copy(func):
    def wrapper(n):
        return func(n).copy()
    return wrapper


@cache_copy
@cache
def pfactor(n: Decimal) -> list[Decimal]:
    # TODO rework this
    if n == 1: return [Decimal(1)]
    if n == -1: return [Decimal(-1)]
    if n == 0: return [Decimal(0)]
    global primes
    if n < 0:
        factors = [Decimal(-1)]
        n *= -1
    else:
        factors = []
    while n != 1:
        for p in primes:
            if not n % p:
                n /= p
                factors.append(Decimal(p))
                break
        else:
            i = primes[-1]
            while True:
                i += 1
                if isprime(i):
                    primes.append(i)
                    if not n % i:
                        n /= i
                        factors.append(Decimal(i))
                        break
    return factors

if __name__ == '__main__':
    pass