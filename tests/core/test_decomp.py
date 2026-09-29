import pytest
from CAS.core.expr import *

from collections import Counter


class TestNumDecomp:
    def test_small_prime(self):
        assert Num(7).decomp() == Counter({Num(7): Num(1)})

    def test_large_prime(self):
        assert Num(2971215073).decomp() == Counter({Num(2971215073): Num(1)})

    def test_small_composite(self):
        assert Num(360).decomp() == Counter({Num(2): Num(3), Num(3): Num(2), Num(5): Num(1)})

    def test_large_composite(self):
        ans = Counter({Num(2): Num(18),
                       Num(3): Num(8),
                       Num(5): Num(4),
                       Num(7): Num(2),
                       Num(11): Num(1),
                       Num(13): Num(1),
                       Num(17): Num(1),
                       Num(19): Num(1)})
        assert Num(2432902008176640000).decomp() == ans


class TestVarDecomp:
    def test(self, x):
        assert x.decomp() == Counter({x: Num(1)})


class TestSumDecomp:
    def test(self, x):
        assert Sum([x, 1]).decomp() == Counter({Sum([x, 1]): Num(1)})


class TestExpDecomp:
    def test_pow_integer(self, x):
        assert (x**2).decomp() == Counter({x: Num(2)})

    def test_pow_noninteger(self, x):
        assert (x**1.5).decomp() == Counter({x: Frac(Num(3), Num(2))})

    def test_nested_exp(self, x):
        assert ((x**3)**2).decomp() == Counter({x: Num(6)})