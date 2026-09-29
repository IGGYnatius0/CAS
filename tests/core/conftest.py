import pytest
from CAS.core import Var, Exp


@pytest.fixture
def x():
    return Var('x')


@pytest.fixture
def y():
    return Var('y')


@pytest.fixture
def z():
    return Var('z')

@pytest.fixture
def sqrt2():
    return Exp(2, Exp(2, -1))