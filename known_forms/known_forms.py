from forms.abc import *

# TODO implement a single object containing both form and formula, similar to RewriteRule

# Polynomial
linear    = A * x + B
quadratic = A * x ** 2 + B * x + C
cubic     = A * x ** 3 + B * x ** 2 + C * x + D
quartic   = A * x ** 4 + B * x ** 3 + C * x ** 2 + D * x + E
poly = [linear, quadratic, cubic, quartic]


FORMS = [*poly]

for i, form in enumerate(FORMS):
    FORMS[i] = form.group_consts()