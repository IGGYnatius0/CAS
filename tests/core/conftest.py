import pytest
from CAS.core import Var, Exp


@pytest.fixture
def sqrt2():
    return Exp(2, Exp(2, -1))