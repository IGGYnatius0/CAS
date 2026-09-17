from .registry import FORMS

from .base import FormExprBase
from .utils import *
import CAS.forms.expr.num
import CAS.forms.expr.const
import CAS.forms.expr.wild
import CAS.forms.expr.var
import CAS.forms.expr.sum
import CAS.forms.expr.prod
import CAS.forms.expr.frac
import CAS.forms.expr.exp
import CAS.forms.expr.eqn
import CAS.forms.expr.constraints


FormNum = FORMS.num
FormConst = FORMS.const
FormVar = FORMS.var
FormWild = FORMS.wild
FormSum = FORMS.sum
FormProd = FORMS.prod
FormFrac = FORMS.frac
FormExp = FORMS.exp
FormEqn = FORMS.eqn

fzero = FORMS.zero
fone = FORMS.one
fneg_one = FORMS.neg_one


__all__ = ['FormExprBase',
           'FormNum', 'FormConst', 'FormVar', 'FormWild',
           'FormSum', 'FormProd', 'FormFrac', 'FormExp', 'FormEqn',
           'fzero', 'fone', 'fneg_one',
           'make_form', 'core2form', 'form2core']