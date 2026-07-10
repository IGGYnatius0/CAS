from .abc import *

# Polynomial
linear    = -B / A
quadratic = [(-B + (B**2 - 4*A*C) ** 0.5) / (2*A), (-B - (B**2 - 4*A*C) ** 0.5) / (2*A)]
cubic     = 0
quartic   = 0

poly = [linear, quadratic, cubic, quartic]

FORMULAS = [*poly]