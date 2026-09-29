from CAS.core import *


class TestNumVarSimplify:
    def test_num(self):
        assert simplify(Num(1)) == Num(1)

    def test_var(self, x):
        assert simplify(x) == x


class TestExpSimplify:
    def test_pow_one(self, x):
        assert simplify(Exp(x, 1)) == x

    def test_pow_zero(self, x):
        assert simplify(Exp(x, 0)) == one

    def test_base_zero(self, x):
        assert simplify(Exp(0, x)) == zero

    def test_args_integer(self):
        assert simplify(Exp(2, 3)) == Num(8)

    def test_pow_noninteger(self):
        assert simplify(Exp(2, Exp(2, -1))) == Exp(2, Exp(2,-1))

    def test_root(self):
        assert simplify(Exp(8, Exp(3, -1))) == Num(2)

    def test_base_noninteger(self):
        assert simplify(Exp(Exp(2, -1), 2)) == Exp(2, -2)

    def test_args_noninteger(self):
        assert simplify(Exp(0.5, 0.5)) == Exp(2, Prod([-1, Exp(2, -1)]))

    def test_special(self, sqrt2):
        assert simplify(Exp(Exp(sqrt2, sqrt2), sqrt2)) == Num(2)


class TestFracSimplify:
    def test_nums(self):
        assert simplify(Frac(5, 6)) == Prod([Num(5), Exp(6, -1)])

    def test_simplest_form(self):
        assert simplify(Frac(48, 6)) == Num(8)

    def test_numer_zero(self):
        assert simplify(Frac(0, 1)) == Num(0)

    def test_denom_one(self):
        assert simplify(Frac(5, 1)) == Num(5)


class TestProdSimplify:
    def test_nums(self):
        assert simplify(Prod([1, 2, 3, 4, 5])) == Num(120)

    def test_vars_easy(self, x, y):
        assert simplify((x * y)) == x * y

    def test_vars_hard(self, x, y):
        assert simplify((x**3 * y**-1 * x**-5 * y**2)) == x**-2 * y

    def test_nums_vars(self, x, y):
        assert simplify((4 * x**3 * y**-1 * x**-5 * y**2 * 0.5)) == 2 * x**-2 * y

    def test_one(self, x):
        assert simplify((x * 1)) == x

    def test_zero(self, x):
        assert simplify((x * 0)) == zero

    def test_empty(self):
        assert simplify(Prod([])) == one


class TestSumSimplify:
    def test_nums_integer(self):
        assert simplify(Sum([1, -2, 3, -4, 5])) == Num(3)

    def test_nums_rational(self):
        assert simplify((Frac(1, 2) + Frac(2, 3) + Frac(3, 5))) == 53 * Exp(30, -1)

    def test_vars(self, x, y):
        assert simplify((x + y)) == x + y

    def test_surd(self, sqrt2):
        assert simplify(sqrt2 + sqrt2) == Exp(2, 3 * Exp(2, -1))

    def test_coeffs_integer(self, x, y):
        assert simplify((3*x - y - 5*x + 2*y)) == -2*x + y

    def test_coeffs_rational(self, x, y):
        assert simplify((1.5*x + Frac(4, 3)*x)) == (17 * Exp(6, -1)) * x

    def test_coeffs_hard(self, x, sqrt2):
        assert simplify(((sqrt2+1) * x + Frac(2, 3) * x)) == (5 * Exp(3, -1) + sqrt2) * x

    def test_zero(self, x):
        assert simplify((x + 0)) == x

    def test_empty(self, x):
        assert simplify(Sum([x])) == x