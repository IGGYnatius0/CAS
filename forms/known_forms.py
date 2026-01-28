from core.core_classes import zero
from forms.abc import *
from forms.form_classes import FormEqn

# Polynomial
_linear = FormEqn(A * x + B, zero)
_quadratic = FormEqn(A * x ** 2 + B * x + C, zero)
_cubic = FormEqn(A * x ** 3 + B * x ** 2 + C * x + D, zero)
_quartic = FormEqn(A * x ** 4 + B * x ** 3 + C * x ** 2 + D * x + E, zero)

forms = [_linear, _quadratic, _cubic, _quartic]