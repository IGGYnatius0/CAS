from .registry import FORMS

from .base import FormExprBase
from .utils import *
import CAS.form.expr.num
import CAS.form.expr.const
import CAS.form.expr.wild
import CAS.form.expr.var
import CAS.form.expr.sum
import CAS.form.expr.prod
import CAS.form.expr.frac
import CAS.form.expr.exp
import CAS.form.expr.eqn
import CAS.form.expr.constraints


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