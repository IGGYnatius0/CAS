from core.core_classes import *
from forms.form_classes import *


class RewriteRule:
    def __init__(self, match_fn):
        self.match_fn = match_fn
    
    def match(self, expr):
        return self.match_fn(expr)
    