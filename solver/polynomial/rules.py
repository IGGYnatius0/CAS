from forms.classes import FormEqn
from forms.abc import *
from solver.base import *


rules = SolveGroup((
    SolveRule(
        target_form=A*x+B,
        formula=-B/A
    ),

    SolveRule(
        target_form=A*x**2+B*x+C,
        formula=((-B+(B**2-4*A*C)**0.5)/(2*A),
                 (-B-(B**2-4*A*C)**0.5)/(2*A))
    )
))

