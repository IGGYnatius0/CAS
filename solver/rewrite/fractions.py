from solver.rewrite.base import *
from forms.abc import *
from core.num import *


rules = RewriteGroup((
    RewriteSet((
        a1*(a2/a3),
        (a1*a2)/a3
    )),
    RewriteSet((
        one/(a1/a2),
        a2/a1
    )),
    RewriteRule( # TODO generalised version
        form=(a1/a2)*(a3/a4),
        target=(a1*a3)/(a2*a4)
    ),
    RewriteRule( # TODO generalised version
        form=(a1/a2)+(a3/a4),
        target=(a1*a3+a2*a3)/(a2*a4)
    ),
    RewriteSet((
        (a1/a2)/a3,
        (a1/a2)*(one/a3)
    )),
    RewriteSet((
        a1/(a2/a3),
        a1*(a3/a2)
    )),
    RewriteSet((
        (a1/a2)/(a3/a4),
        (a1/a2)*(a4/a3)
    ))
))