from CAS.core import *

from collections import Counter


class TestNumDecomp:
    def test_small_prime(self):
        assert decomp(Num(7)) == Counter({Num(7): Num(1)})

    def test_large_prime(self):
        assert decomp(Num(2971215073)) == Counter({Num(2971215073): Num(1)})

    def test_small_composite(self):
        assert decomp(Num(360)) == Counter({Num(2): Num(3), Num(3): Num(2), Num(5): Num(1)})

    def test_large_composite(self):
        ans = Counter({Num(2): Num(18),
                       Num(3): Num(8),
                       Num(5): Num(4),
                       Num(7): Num(2),
                       Num(11): Num(1),
                       Num(13): Num(1),
                       Num(17): Num(1),
                       Num(19): Num(1)})

        # 20 factorial
        assert decomp(Num(2432902008176640000)) == ans


class TestVarDecomp:
    def test(self, x):
        assert decomp(x) == Counter({x: Num(1)})


class TestSumDecomp:
    def test(self, x):
        assert decomp(Sum([x, 1])) == Counter({Sum([x, 1]): Num(1)})


class TestProdDecomp:
    def test(self, x, y):
        assert decomp(x * y * x**3 * y**-3) == Counter({x: Num(4), y: Num(-2)})


class TestExpDecomp:
    def test_pow_integer(self, x):
        assert decomp((x**2)) == Counter({x: Num(2)})

    def test_pow_noninteger(self, x):
        assert decomp((x**1.5)) == Counter({x: Prod([3, Exp(2, -1)])})

    def test_nested_exp(self, x):
        assert decomp(((x**3)**2)) == Counter({x: Num(6)})