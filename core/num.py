from decimal import Decimal
from utils import pfactor

# TODO force frac and exp of Nums to remain symbolic instead of getting evaluated

def _num_check(func):
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        if Num.isnum(f):
            return Num(f)
        return f
    return wrapper


class _NumTemplate(Decimal):
    __add__ = _num_check(Decimal.__add__)
    __radd__ = _num_check(Decimal.__radd__)
    __sub__ = _num_check(Decimal.__sub__)
    __rsub__ = _num_check(Decimal.__rsub__)
    __mul__ = _num_check(Decimal.__mul__)
    __rmul__ = _num_check(Decimal.__rmul__)
    __truediv__ = _num_check(Decimal.__truediv__)
    __rtruediv__ = _num_check(Decimal.__rtruediv__)
    __mod__ = _num_check(Decimal.__mod__)
    __rmod__ = _num_check(Decimal.__rmod__)
    __pow__ = _num_check(Decimal.__pow__)
    __rpow__ = _num_check(Decimal.__rpow__)
    __neg__ = _num_check(Decimal.__neg__)
    __pos__ = _num_check(Decimal.__pos__)


class Num(_NumTemplate):
    def __init__(self, value, *args, **kwargs):
        Decimal.__init__(str(value), *args, **kwargs)

    def decomp(self):
        if self.to_integral_value() == self:
            return [Num(n) for n in pfactor(self)]
        return [self]

    def group(self):
        return self

    def simplify(self, auto_factorise=True):
        return self

    @classmethod
    def isnum(cls, expr):
        return isinstance(expr, (int, float, Decimal, Num))

    def __repr__(self):
        return f"Num({str(self)})"

    def __hash__(self):
        return hash(('CoreNum', super().__hash__()))

neg_one = Num(-1)
zero = Num(0)
one = Num(1)
