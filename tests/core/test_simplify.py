"""Tests for src/CAS/expr/*"""
from collections import Counter
from decimal import Decimal

import pytest
from CAS.core.expr import *


"""
test simplify

exp simplify
- pow=1
- pow=0, base!=0
- base=0, power!=0
- base integer, pow integer
- base integer, pow non integer (eg sqrt2)
- base non integer, pow integer
- base non integer, pow non integer
- (eg (sqrt2 ^ sqrt2) ^ sqrt2)

prod simplify
...???
"""

@pytest.fixture
def x():
    return Var("x")


@pytest.fixture
def y():
    return Var("y")


class TestExpSimplify:
    def test_pow_one(self, x):
        assert Exp(x, one).simplify() == x

    def test_pow_zero(self, x):
        assert Exp(x, zero).simplify() == one

    def test_base_zero(self, x):
        assert Exp(zero, x).simplify() == zero

    def test_args_integer(self):
        assert Exp(Num(2), Num(3)).simplify() == Num(8)

    def test_pow_noninteger(self):
        assert Exp(Num(2), Exp(Num(2), neg_one)).simplify() == Exp(Num(2), Exp(Num(2), neg_one))

    def test_root(self):
        assert Exp(Num(8), Exp(Num(3), neg_one)).simplify() == Num(2)

    def test_base_noninteger(self):
        assert Exp(Exp(Num(2), neg_one), Num(2)).simplify() == Exp(Num(2), Num(-2))

    def test_args_noninteger(self):
        assert Exp(0.5, 0.5).simplify() == Exp(Num(2), Prod([Num(-1), Exp(Num(2), Num(-1))]))

    def test_special(self):
        sqrt2 = Exp(Num(2), Exp(Num(2), neg_one))
        assert Exp(Exp(sqrt2, sqrt2), sqrt2).simplify() == Num(2)

class TestFracSimplify:
    pass