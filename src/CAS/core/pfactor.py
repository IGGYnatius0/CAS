from math import gcd
from random import randint
from collections import Counter
from functools import lru_cache


__all__ = ['pfactor']


# From https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Miller%E2%80%93Rabin_test
def miller_rabin(n, k=4):
    if not n % 2:
        return False
    if not n % 3:
        return False
    d = n
    q = (n-1) / 2
    s = 0
    while int(q) == q:
        d = q
        q = d / 2
        s += 1
    d = int(d)

    for i in range(k):
        a = randint(2, int(n)-2)
        x = pow(a, d, n)
        for j in range(s):
            y = pow(x, 2, n)
            if y == 1 and x != 1 and x != n-1:
                return False
            x = y
        if y != 1:
            return False
    return True


# From https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm#Algorithm
def pollard_rho(n, c=1):
    if not n % 2:
        return 2
    if not n % 3:
        return 3
    x = 2
    y = x
    d = 1
    while d == 1:
        x = (x*x+c) % n
        y = (y*y+c) % n
        y = (y*y+c) % n
        d = gcd(int(abs(x-y)), int(n))
    if d != n:
        return d
    return None


@lru_cache(maxsize=1000)
def _pfactor(n):
    if n == 2:
        return Counter({2: 1})
    if n == 3:
        return Counter({3: 1})
    if miller_rabin(n):
        return Counter({n: 1})
    f1 = None
    seed = 1
    while f1 is None:
        f1 = pollard_rho(n, seed)
        seed += 1
    f2 = n // f1
    return _pfactor(f1) + _pfactor(f2)


def pfactor(n):
    if n == 0:
        return Counter({0: 1})
    if n == 1:
        return Counter({1: 1})
    if n == -1:
        return Counter({-1: 1})
    if n < 0:
        return (_pfactor(-n) + Counter({-1: 1})).copy()
    return _pfactor(n).copy()


if __name__ == '__main__':
    # print(pfactor(Decimal(-1350851717672992095)))
    f= pfactor(24)
    print(f)