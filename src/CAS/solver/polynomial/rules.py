from CAS.form import FormConst, FormVar
from ..base import *


a = FormConst('a')
b = FormConst('b')
c = FormConst('c')
x = FormVar('x')


rules = SolveGroup(( # TODO cubic, quartic and general case
    SolveRule(
        target_form=a*x+b,
        formula=-b/a
    ),

    SolveRule(
        target_form=a*x**2+b*x+c,
        formula=((-b+(b**2-4*a*c)**0.5)/(2*a),
                 (-b-(b**2-4*a*c)**0.5)/(2*a))
    )
))

