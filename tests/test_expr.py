"""Tests for src/CAS/expr/*"""
from collections import Counter
from decimal import Decimal

import pytest
from CAS.core.expr import *

inf = Num('inf')
ninf = -inf
neg_one = Num(-1)
one = Num(1)
zero = Num(0)


@pytest.fixture
def x():
    return Var("x")


@pytest.fixture
def y():
    return Var("y")


# ---------------------------------------------------------------------------
# constants / Num basics
# ---------------------------------------------------------------------------

class TestConstants:
    def test_zero_one_neg_one(self):
        assert zero == Num(0)
        assert one == Num(1)
        assert neg_one == Num(-1)

    def test_inf(self):
        assert inf == Num("inf")
        assert ninf == -Num("inf")

    def test_is_num(self):
        assert Num.is_num(1)
        assert Num.is_num(1.5)
        assert Num.is_num(Decimal("2"))
        assert Num.is_num(Num(3))
        assert not Num.is_num(Var("x"))
        assert not Num.is_num("a")
        assert not Num.is_num(None)

    def test_num_arithmetic_wraps_num(self):
        result = Num(1) + Num(2)
        assert isinstance(result, Num)
        assert result == Num(3)

    def test_num_neg_one_hash_avoids_collision(self):
        assert hash(Num(-1)) != hash(Num(-2))
        assert Num(-1) == Num(-1)


class TestConstructors:
    def test_sum_coerces_raw_numbers(self):
        s = Sum([1, 2.5])
        assert s.terms == [Num(1), Num("2.5")]

    def test_prod_coerces_raw_numbers(self, x):
        p = Prod([2, x])
        assert p.factors == [Num(2), x]

    def test_sum_flattens_nested(self, x):
        assert Sum([Sum([x, Num(1)]), Num(2)]).terms == [x, Num(1), Num(2)]

    def test_prod_flattens_nested(self, x):
        assert Prod([Prod([x, Num(2)]), Num(3)]).factors == [x, Num(2), Num(3)]

    def test_sum_skips_none_and_empty(self, x):
        assert Sum([x, None, []]).terms == [x]

    def test_prod_skips_none_and_empty(self, x):
        assert Prod([x, None, []]).factors == [x]

    def test_empty_sum_is_zero(self):
        assert Sum([]).terms == [zero]

    def test_empty_prod_is_one(self):
        assert Prod([]).factors == [one]

    def test_frac_wraps_numbers(self, x):
        f = Frac(1, x)
        assert f.numer == Num(1)
        assert f.denom == x

    def test_exp_wraps_numbers(self, x):
        e = Exp(x, 2)
        assert e.power == Num(2)


# ---------------------------------------------------------------------------
# decomp() — thorough
# ---------------------------------------------------------------------------

class TestNumDecomp:
    def test_prime_powers(self):
        assert Num(12).decomp() == Counter({Num(2): Num(2), Num(3): Num(1)})

    def test_prime(self):
        assert Num(13).decomp() == Counter({Num(13): Num(1)})

    def test_one(self):
        assert Num(1).decomp() == Counter({Num(1): Num(1)})

    def test_zero(self):
        assert Num(0).decomp() == Counter({Num(0): Num(1)})

    def test_minus_one(self):
        assert Num(-1).decomp() == Counter({Num(-1): Num(1)})

    def test_negative_int_includes_minus_one(self):
        assert Num(-12).decomp() == Counter(
            {Num(2): Num(2), Num(3): Num(1), Num(-1): Num(1)}
        )

    def test_non_integer_uses_integer_ratio(self):
        # 1.5 == 3/2
        assert Num("1.5").decomp() == Counter({Num(3): Num(1), Num(2): Num(-1)})


class TestVarDecomp:
    def test_var_decomposes_to_itself(self, x):
        assert x.decomp() == Counter({x: one})


class TestSumDecomp:
    def test_sum_uses_default_decomp(self, x):
        s = Sum([x, Num(2)])
        assert s.decomp() == Counter({s: one})


class TestProdDecomp:
    def test_merges_factor_decomps(self, x):
        assert Prod([x, x**2]).decomp() == Counter({x: Num(3)})

    def test_numeric_factors_merge(self):
        assert Prod([Num(6), Num(10)]).decomp() == Counter(
            {Num(2): Num(2), Num(3): Num(1), Num(5): Num(1)}
        )

    def test_mixed_symbolic_numeric(self, x):
        assert Prod([Num(6), x]).decomp() == Counter(
            {Num(2): Num(1), Num(3): Num(1), x: Num(1)}
        )


class TestFracDecomp:
    def test_numeric_fraction(self):
        # 6/4 == 3/2
        assert Frac(Num(6), Num(4)).decomp() == Counter(
            {Num(3): Num(1), Num(2): Num(-1)}
        )

    def test_symbolic_cancellation(self, x):
        assert Frac(x**2, x).decomp() == Counter({x: Num(1)})

    def test_subtracts_denom_decomp(self, x, y):
        assert Frac(x, y).decomp() == Counter({x: Num(1), y: Num(-1)})


class TestExpDecomp:
    def test_numeric_power(self, x):
        assert Exp(x, Num(2)).decomp() == Counter({x: Num(2)})

    def test_negative_numeric_power(self, x):
        assert Exp(x, Num(-1)).decomp() == Counter({x: Num(-1)})

    def test_symbolic_power_decomposes_to_self(self, x, y):
        e = Exp(x, y)
        assert e.decomp() == Counter({e: 1})


class TestDecomp2Prod:
    def test_single_entry(self, x):
        assert decomp2prod(Counter({x: Num(2)})) == Prod([Exp(x, Num(2))])

    def test_empty_counter_is_one(self):
        assert decomp2prod(Counter()) == Prod([Num(1)])

    def test_round_trip(self, x):
        expr = Prod([Num(6), x])
        assert decomp2prod(expr.decomp()).simplify() == expr.simplify()


# ---------------------------------------------------------------------------
# simplify() — thorough
# ---------------------------------------------------------------------------

class TestNumVarSimplify:
    def test_num_identity(self):
        assert Num(5).simplify() == Num(5)

    def test_var_identity(self, x):
        assert x.simplify() == x


class TestSumSimplify:
    def test_like_terms_combine(self, x):
        assert Sum([x, x]).simplify() == Prod([Num(2), x])

    def test_zero_eliminated(self, x):
        assert Sum([x, zero]).simplify() == x

    def test_all_zero_is_zero(self):
        assert Sum([zero, zero]).simplify() == zero

    def test_coefficients_combine_with_constant(self, x):
        result = Sum([Num(2), Prod([Num(3), x]), Prod([Num(4), x])]).simplify()
        assert result == Sum([Num(2), Prod([Num(7), x])])

    def test_single_term_unwraps(self, x):
        assert Sum([x]).simplify() == x

    def test_fractions_combine_to_equivalent_value(self, x):
        combined = Sum([Frac(x, Num(2)), Frac(x, Num(3))]).simplify()
        # x/2 + x/3 == 5*x/6; internal form keeps negative powers, so
        # compare via difference simplifying to zero.
        assert (combined - Frac(Prod([Num(5), x]), Num(6))).simplify() == zero

    def test_cancellation_to_zero(self, x):
        assert Sum([x, Prod([neg_one, x])]).simplify() == zero

    def test_numeric_sum_folds(self):
        assert Sum([Num(2), Num(3)]).simplify() == Num(5)


class TestProdSimplify:
    def test_zero_annihilates(self, x):
        assert Prod([zero, x]).simplify() == zero

    def test_constants_fold(self, x):
        assert Prod([Num(2), Num(3), x]).simplify() == Prod([Num(6), x])

    def test_all_constants_fold(self):
        assert Prod([Num(2), Num(3)]).simplify() == Num(6)

    def test_one_single_factor_unwraps(self, x):
        assert Prod([one, x]).simplify() == x

    def test_one_multi_factor_dropped(self, x, y):
        assert Prod([one, x, y]).simplify() == Prod([x, y])

    def test_single_factor_unwraps(self, x):
        assert Prod([x]).simplify() == x

    def test_zero_const_with_no_factors(self):
        assert Prod([zero]).simplify() == zero


class TestFracSimplify:
    def test_numeric_reduction(self):
        assert Frac(Num(6), Num(4)).simplify() == Frac(Num(3), Num(2)).simplify()

    def test_symbolic_cancellation(self, x):
        assert Frac(x**2, x).simplify() == x

    def test_identity(self, x):
        assert Frac(x, x).simplify() == one

    def test_numer_simplify_applies(self, x):
        assert Frac(Sum([x, x]), Num(2)).simplify() == x


class TestExpSimplify:
    def test_power_one_returns_base(self, x):
        assert Exp(x, one).simplify() == x

    def test_power_zero_returns_one(self, x):
        assert Exp(x, zero).simplify() == one

    def test_one_base_returns_one(self, y):
        assert Exp(one, y).simplify() == one

    def test_zero_base_positive_power(self):
        assert Exp(zero, Num(2)).simplify() == zero

    def test_zero_to_zero_preserved(self):
        assert Exp(zero, zero).simplify() == Exp(zero, zero)

    def test_integer_power_folds(self):
        assert Exp(Num(2), Num(3)).simplify() == Num(8)

    def test_negative_power_stays_symbolic(self):
        assert Exp(Num(2), Num(-1)).simplify() == Exp(Num(2), Num(-1))

    def test_fractional_power_exact_root_folds(self):
        assert Exp(Num(9), Num("0.5")).simplify() == Num(3)

    def test_symbolic_stays(self, x, y):
        assert Exp(x, y).simplify() == Exp(x, y)


# ---------------------------------------------------------------------------
# expand / factorize (lighter)
# ---------------------------------------------------------------------------

class TestExpand:
    def test_prod_distributes_over_sum(self, x):
        result = Prod([Sum([x, Num(1)]), Sum([x, Num(2)])]).expand()
        expected = Sum(
            [
                Prod([x, x]),
                Prod([x, Num(2)]),
                Prod([Num(1), x]),
                Prod([Num(1), Num(2)]),
            ]
        )
        assert result == expected

    def test_exp_positive_int_unrolls(self, x):
        assert Exp(x, Num(2)).expand() == Sum([Prod([x, x])])

    def test_exp_symbolic_unchanged(self, x, y):
        assert Exp(x, y).expand() == Exp(x, y)

    def test_exp_negative_unchanged(self, x):
        assert Exp(x, Num(-1)).expand() == Exp(x, Num(-1))

    def test_sum_recurses(self, x):
        assert Sum([Exp(x, Num(2)), Num(1)]).expand() == Sum(
            [Sum([Prod([x, x])]), Num(1)]
        ) or Sum([Exp(x, Num(2)), Num(1)]).expand() == Sum(
            [Prod([x, x]), Num(1)]
        )

    def test_num_var_identity(self, x):
        assert Num(3).expand() == Num(3)
        assert x.expand() == x


class TestFactorize:
    def test_sum_extracts_common_factor(self, x):
        factored = Sum([x**2, x]).factorize().simplify()
        assert (factored - Prod([x, Sum([x, one])])).simplify() == zero

    def test_common_numeric_factor(self, x):
        factored = Sum([Prod([Num(2), x]), Prod([Num(3), x])]).factorize().simplify()
        assert factored == Prod([Num(5), x])

    def test_prod_recurses(self, x):
        assert Prod([Sum([x**2, x]), Num(2)]).factorize() == Prod(
            [Sum([x**2, x]).factorize(), Num(2)]
        )

    def test_num_var_identity(self, x):
        assert Num(3).factorize() == Num(3)
        assert x.factorize() == x


# ---------------------------------------------------------------------------
# substitute_vars / get_vars / isnum / copy
# ---------------------------------------------------------------------------

class TestSubstituteVars:
    def test_var_hit(self, x):
        assert x.substitute_vars({x: Num(5)}) == Num(5)

    def test_var_miss_returns_self(self, x, y):
        assert x.substitute_vars({y: Num(1)}) == x

    def test_num_returns_self(self):
        assert Num(3).substitute_vars({Var("x"): Num(1)}) == Num(3)

    def test_sum_recurses(self, x, y):
        assert Sum([x, y]).substitute_vars({x: Num(5)}) == Sum([Num(5), y])

    def test_prod_recurses(self, x, y):
        assert Prod([x, y]).substitute_vars({x: Num(5)}) == Prod([Num(5), y])

    def test_frac_recurses(self, x, y):
        assert Frac(x, y).substitute_vars({x: Num(2)}) == Frac(Num(2), y)

    def test_exp_recurses(self, x, y):
        assert Exp(x, y).substitute_vars({y: Num(2)}) == Exp(x, Num(2))


class TestGetVars:
    def test_num_empty(self):
        assert Num(5).get_vars == set()

    def test_var_singleton(self, x):
        assert x.get_vars == {x}

    def test_sum_union(self, x, y):
        assert Sum([x, y]).get_vars == {x, y}

    def test_prod_union(self, x, y):
        assert Prod([x, y]).get_vars == {x, y}

    def test_frac_union(self, x, y):
        assert Frac(x, y).get_vars == {x, y}

    def test_exp_union(self, x, y):
        assert Exp(x, y).get_vars == {x, y}


class TestIsNum:
    def test_num_true(self):
        assert Num(5).isnum is True

    def test_var_false(self, x):
        assert x.isnum is False

    def test_sum_all_numeric(self):
        assert Sum([Num(1), Num(2)]).isnum is True

    def test_sum_with_var_false(self, x):
        assert Sum([Num(1), x]).isnum is False

    def test_prod_all_numeric(self):
        assert Prod([Num(2), Num(3)]).isnum is True

    def test_prod_with_var_false(self, x):
        assert Prod([Num(2), x]).isnum is False

    def test_frac_numeric(self):
        assert Frac(Num(1), Num(2)).isnum is True

    def test_frac_symbolic_false(self, x):
        assert Frac(x, Num(2)).isnum is False

    def test_exp_numeric(self):
        assert Exp(Num(2), Num(3)).isnum is True

    def test_exp_symbolic_false(self, x):
        assert Exp(x, Num(2)).isnum is False


class TestCopy:
    def test_var_copy_equal_but_distinct(self, x):
        c = x.copy()
        assert c == x
        assert c is not x

    def test_sum_copy_independent(self, x, y):
        s = Sum([x, Num(1)])
        c = s.copy()
        assert c == s
        s.terms.append(y)
        assert c != s

    def test_prod_copy_independent(self, x, y):
        p = Prod([x, Num(2)])
        c = p.copy()
        p.factors.append(y)
        assert c != p

    def test_frac_copy(self, x):
        f = Frac(x, Num(2))
        assert f.copy() == f

    def test_exp_copy(self, x):
        e = Exp(x, Num(2))
        assert e.copy() == e

    def test_num_copy_identity(self):
        assert Num(5).copy() == Num(5)


# ---------------------------------------------------------------------------
# eval_nums / group_nums (correct behavior; known Prod.eval_nums bug xfailed)
# ---------------------------------------------------------------------------

class TestEvalNums:
    def test_num_identity(self):
        assert Num(3).eval_nums() == Num(3)

    def test_sum_folds_numerics(self, x):
        assert Sum([Num(2), Num(3), x]).eval_nums() == Sum([x, Num(5)])

    def test_sum_all_numeric(self):
        assert Sum([Num(2), Num(3)]).eval_nums() == Num(5)

    def test_sum_no_numeric_unchanged(self, x):
        assert Sum([x]).eval_nums() == Sum([x])

    @pytest.mark.xfail(
        reason="Prod.eval_nums adds numeric factors instead of multiplying "
        "(classes.py uses num += ...); e.g. Prod([2,4]) gives 7 not 8"
    )
    def test_prod_folds_numerics(self, x):
        assert Prod([Num(2), Num(4), x]).eval_nums() == Prod([x, Num(8)])

    @pytest.mark.xfail(
        reason="Prod.eval_nums adds numeric factors instead of multiplying; "
        "Prod([2,4]) gives 7 not 8"
    )
    def test_prod_all_numeric(self):
        assert Prod([Num(2), Num(4)]).eval_nums() == Num(8)

    def test_frac_eval(self):
        assert Frac(Num(2), Num(4)).eval_nums() == Num("0.5")

    def test_exp_eval(self):
        assert Exp(Num(2), Num(3)).eval_nums() == Num(8)


class TestGroupNums:
    def test_sum_groups_numerics_to_end(self, x):
        grouped = Sum([Num(2), x, Num(3)]).group_nums()
        assert grouped.terms[0] == x
        assert grouped.terms[1] == Sum([Num(3), Num(2)])

    def test_prod_groups_numerics_to_end(self, x):
        grouped = Prod([Num(2), x, Num(3)]).group_nums()
        assert grouped.factors[0] == x
        assert grouped.factors[1] == Prod([Num(3), Num(2)])

    def test_sum_all_numeric_returns_self(self):
        s = Sum([Num(1), Num(2)])
        assert s.group_nums() == s

    def test_prod_all_numeric_returns_self(self):
        p = Prod([Num(2), Num(3)])
        assert p.group_nums() == p

    def test_frac_recurses(self, x):
        assert Frac(Sum([Num(1), x]), Num(2)).group_nums() == Frac(
            Sum([Num(1), x]).group_nums(), Num(2)
        )

    def test_exp_recurses(self, x):
        assert Exp(Sum([Num(1), x]), Num(2)).group_nums() == Exp(
            Sum([Num(1), x]).group_nums(), Num(2)
        )


# ---------------------------------------------------------------------------
# equality / hashing / repr / str
# ---------------------------------------------------------------------------

class TestEqualityHashing:
    def test_sum_order_insensitive(self, x):
        assert Sum([x, Num(1)]) == Sum([Num(1), x])
        assert hash(Sum([x, Num(1)])) == hash(Sum([Num(1), x]))

    def test_prod_order_insensitive(self, x, y):
        assert Prod([x, y]) == Prod([y, x])
        assert hash(Prod([x, y])) == hash(Prod([y, x]))

    def test_cross_type_inequality(self, x):
        assert (x == Num(1)) is False
        assert (x == "x") is False
        assert (Sum([x]) == Prod([x])) is False

    def test_frac_order_sensitive(self, x, y):
        assert Frac(x, y) != Frac(y, x)

    def test_exp_order_sensitive(self, x, y):
        assert Exp(x, y) != Exp(y, x)

    def test_core_expr_membership(self, x):
        for expr in (Num(1), x, Sum([x]), Prod([x]), Frac(x, one), Exp(x, one)):
            assert isinstance(expr, CoreBaseExpr)


class TestStrRepr:
    def test_var(self, x):
        assert str(x) == "x"
        assert repr(x) == "Var('x')"

    def test_sum(self, x):
        assert str(Sum([x, Num(1)])) == "(x + 1)"
        assert repr(Sum([x, Num(1)])) == "Sum([Var('x'), Num(1)])"

    def test_prod(self, x):
        assert str(Prod([x, Num(2)])) == "(x * 2)"

    def test_frac(self, x):
        assert str(Frac(x, Num(2))) == "(x / 2)"
        assert repr(Frac(x, Num(2))) == "Frac(Var('x'), Num(2))"

    def test_exp(self, x):
        assert str(Exp(x, Num(2))) == "(x ^ 2)"
        assert repr(Exp(x, Num(2))) == "Exp(Var('x'), Num(2))"

    def test_num_repr(self):
        assert repr(Num(5)) == "Num(5)"
