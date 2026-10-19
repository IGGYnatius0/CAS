import pytest
from pytest import param
from collections import Counter

from CAS.core import *


sqrt2 = Exp(2, Exp(2, -1))
# phi = Frac(1 + Exp(5, 0.5), 2)


class TestDecomp:
    @pytest.mark.parametrize(
        'num,expected',
        [
            (7, Counter({Num(7): one})),
            (2971215073, Counter({Num(2971215073): one})),
            (360, Counter({Num(2): Num(3), Num(3): Num(2), Num(5): one})),
            (2432902008176640000,
             Counter({Num(2): Num(18),
                      Num(3): Num(8),
                      Num(5): Num(4),
                      Num(7): Num(2),
                      Num(11): one,
                      Num(13): one,
                      Num(17): one,
                      Num(19): one}))
        ]
    )
    def test_num(self, num, expected):
        assert decomp(Num(num)) == expected


    @pytest.mark.parametrize(
        'expr,expected',
        [
            (x ** 2, Counter({x: Num(2)})),
            (x ** 1.5, Counter({x: Prod([3, Exp(2, -1)])})),
            ((x ** 3) ** 2, Counter({x: Num(6)})),
            ((x * y ** 2) ** 2, Counter({x: Num(2), y: Num(4)})),
        ]
    )
    def test_exp(self, expr, expected):
        assert decomp(expr) == expected


    @pytest.mark.parametrize(
        'expr,expected',
        [
            (x, Counter({x: one})),
            (Sum([x, 1]), Counter({Sum([x, 1]): one})),
            (x * y * x**3 * y**-3, Counter({x: Num(4), y: Num(-2)})),
            (x / y, Counter({x: one, y: neg_one}))
        ]
    )
    def test_other(self, expr, expected):
        assert decomp(expr) == expected


class TestSimplify:
    def test_num(self):
        assert simplify(Num(1)) == Num(1)


    def test_var(self):
        assert simplify(x) == x


    @pytest.mark.parametrize(
        'sum,expected',
        [
            param(Sum([x]), x, id='single'),
            param(x + 0, x, id='zero'),
            param(one + 2 - 3 + 4 - 5, neg_one, id='integer numbers'),
            param(
                Frac(1, 2) + Frac(2, 3) + Frac(3, 5) - 1,
                23 * Exp(30, -1),
                id='integer rational numbers'),
            param(
                1 + Frac(1, 2) + Frac(1, 3) + sqrt2 + 3 * sqrt2,
                11 * Exp(6, -1) + Exp(2, Prod([5, Exp(2, -1)])),
                id='integer rational irrational numbers'),
            param(
                x + 2 * x - 5 * x - y + 3 * y,
                -2 * x + 2 * y,
                id='integer coefficients with variables'
            ),
            param(
                0.5 * x - Frac(1, 3) * x - x - Frac(2, 3) * y + 0.5 * y + y,
                -5 * Exp(6, -1) * x + 5 * Exp(6, -1) * y,
                id='integer rational coefficients with variables'
            ),
            param(
                0.5 * x + 2 * x + sqrt2 * x - 0.75 * y - y - 3 * sqrt2 * y,
                (5 * Exp(2, -1) + sqrt2) * x + (-7 * Exp(4, -1) + -3 * sqrt2) * y,
                id='integer rational irrational coefficients with variables'
            )
        ]
    )
    def test_sum(self, sum, expected):
        assert simplify(sum) == expected


    @pytest.mark.parametrize(
        'prod,expected',
        [
            param(Prod([x]), x, id='single'),
            param(Prod([-1, 2, -3, 4, -5]), Num(-120), id='integer numbers'),
            param(
                2 * Frac(1, 2) * Frac(3, 4) * Frac(5, 6),
                5 * Exp(8, -1),
                id='integer rational numbers'),
            # param(
            #     2,
            #     id='integer rational irrational numbers'
            # )
            # TODO more cases...
        ]
    )
    def test_prod(self, prod, expected):
        assert simplify(prod) == expected


    @pytest.mark.parametrize(
        'frac,expected',
        [
            param(Frac(2, 3), 2 * Exp(3, -1), id='fraction'),
            param(Frac(10, 2), Num(5), id='simplest form int'),
            param(Frac(10, 4), 5 * Exp(2, -1), id='simplest form frac'),
            param(x ** 5 / x ** 2, x ** 3, id='simplest form var'),
            param(Frac(-2, 1), Num(-2), id='denom 1'),
            param(Frac(0, 1), zero, id='numer 0'),
        ]
    )
    def test_frac(self, frac, expected):
        assert simplify(frac) == expected

    def test_zero_division(self):
        with pytest.raises(ZeroDivisionError):
            simplify(Frac(1, 0))


    @pytest.mark.parametrize(
        'expr,expected',
        [
            param(x ** 1, x, id='pow 1'),
            param(x ** 0, one, id='pow 0'),
            param(1 ** x, one, id='base 1'),
            param(0 ** x, zero, id='base 0'),
            param(Exp(2, 3), Num(8), id='integers'),
            param(Exp(27000, Exp(3, -1)), Num(30), id='root'),
            param(Exp(sqrt2, 2), Num(2), id='base sqrt2'),
            param(Exp(0.5, 0.5), Exp(2, Prod([-1, Exp(2, -1)])), id='args nonint'),
            param(Exp(Exp(sqrt2, sqrt2), sqrt2), Num(2), id='special')
        ]
    )
    def test_exp(self, expr, expected):
        assert simplify(expr) == expected