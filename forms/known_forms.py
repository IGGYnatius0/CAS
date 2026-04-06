from forms.abc import *

# Polynomial
linear    = A * x + B
quadratic = A * x ** 2 + B * x + C
cubic     = A * x ** 3 + B * x ** 2 + C * x + D
quartic   = A * x ** 4 + B * x ** 3 + C * x ** 2 + D * x + E
poly = [linear, quadratic, cubic, quartic]


forms = [*poly]

for i, form in enumerate(forms):
    forms[i] = form.group_consts()