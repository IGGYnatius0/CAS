from collections import Counter

from .registry import EXPRS


def decomp2prod(decomp: Counter) -> EXPRS['prod']:
    return EXPRS['prod']([EXPRS['exp'](base, power) for base, power in decomp.items()])