import pytest
from CAS.core import *
from CAS.function import log


class TestExpand:
    def test_prod(self):
        assert simplify(expand((x+1) * (y-2) * (3*z+4))) == 3*x*y*z + 4*x*y + -6*x*z + -8*x + 3*y*z + 4*y + -6*z + -8
        assert expand(Prod([x])) == Sum([Prod([x])])

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            expand(1)


class TestSubstituteVars:
    def test(self):
        assert substitute_vars(x, {x: one}) == one

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            substitute_vars(1, {})


class TestEvaluate:
    @pytest.mark.parametrize(
        'expr,expected',
        [
            (one, 1),
            (Sum([-1, 2, -3, 4, -5]), -3),
            (Prod([1, 2]), 2),
            (Frac(1, 2), 0.5),
            (Exp(4, 0.5), 2.0),
            (log(2), 0.6931471805599453)
        ]
    )
    def test(self, expr, expected):
        evaluated = evaluate(expr)
        assert evaluated == expected
        assert type(evaluated) == type(expected)

    def test_not_isnum(self):
        with pytest.raises(ValueError):
            evaluate(x)

    def test_eqn(self):
        with pytest.raises(TypeError):
            evaluate(Eqn)

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            evaluate(1)


class TestGroupNums:
    @pytest.mark.parametrize(
        'expr,expected',
        [
            (one, one),
            (x, x),
            (x + 1 + 2, Sum([x, Sum([1, 2])], flatten=False)),
            (x * 2 * 3, Prod([x, Prod([2, 3])], flatten=False))
        ]
    )
    def test(self, expr, expected):
        assert group_nums(expr) == expected

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            group_nums(1)