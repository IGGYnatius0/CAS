import pytest
from CAS.core import *
from CAS.exceptions import BadFunctionError


class TestExpand:
    @pytest.mark.parametrize(
        'expr,expanded',
        [
            ((x+1) * (y-2) * (3*z+4), 3*x*y*z + 4*x*y + -6*x*z + -8*x + 3*y*z + 4*y + -6*z + -8),
            (Prod([x]), Sum([Prod(x)]))
        ]
    )
    def test_prod(self, expr, expanded):
        assert expand(expr) == expanded

    @pytest.mark.parametrize(
        'expr',
        [
            Num(1),
            x,
            x+1,
            x/2,
            x**2
        ]
    )
    def test_other(self, expr):
        assert expand(expr) == expr

    def test_wrong_type(self):
        with pytest.raises(BadFunctionError):
            expand(1)


class TestFactorize:
    @pytest.mark.parametrize(
        'expr,factorized',
        [
            (x + 1, Exp(1, 1) * (x**1 + Exp(1, 1))),
            (x**2 + x, x**1 * (x**1 + 1)),
            (x**2.5*y + x**1.5*y**2, x**1.5 * (x**1 + y**1))
        ]
    )
    def test_sum(self, expr, factorized):
        assert factorize(expr) == factorized

    @pytest.mark.parametrize(
        
    )
    def test_other(self):
        pass