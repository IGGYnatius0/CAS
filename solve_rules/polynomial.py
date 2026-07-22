from forms.classes import FormConst
from forms.abc import *
from solve_rules.base import *


A = FormConst('A', '(0, inf)')


rules = SolveGroup((
    SolveRule(
        target_form=A*x+b,
        formula=-B/A
    ),
    SolveRule(
        target_form=A*x**2+B*x+C,
        formula=((-B+(B**2-4*A*C)**0.5)/(2*A),
                 (-B-(B**2-4*A*C)**0.5)/(2*A))
    ),

    # cubic,
    #
    # quartic,
    #
    # generalised
))