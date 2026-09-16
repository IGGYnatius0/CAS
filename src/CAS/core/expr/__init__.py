from .registry import EXPRS
from .utils import *

from .base import CoreExprBase
import CAS.core.expr.num
import CAS.core.expr.var
import CAS.core.expr.sum
import CAS.core.expr.prod
import CAS.core.expr.frac
import CAS.core.expr.exp
import CAS.core.expr.eqn


Num = EXPRS.num
Var = EXPRS.var
Sum = EXPRS.sum
Prod = EXPRS.prod
Frac = EXPRS.frac
Exp = EXPRS.exp
Eqn = EXPRS.eqn

zero = EXPRS.zero
one = EXPRS.one
neg_one = EXPRS.neg_one
inf = EXPRS.inf
ninf = EXPRS.ninf


__all__ = ['CoreExprBase', 'Num', 'Var', 'Sum', 'Prod', 'Frac', 'Exp', 'Eqn',
           'zero', 'one', 'neg_one', 'inf', 'ninf',
           'decomp2prod', 'make_expr']