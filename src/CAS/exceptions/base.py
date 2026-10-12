__all__ = ['BadMethodError', 'BadFunctionError',
           'MissingVarError', 'MissingConstError']


class CASError(Exception):
    pass


class BadSubroutineError(CASError):
    pass


class BadMethodError(BadSubroutineError):
    pass


class BadFunctionError(BadSubroutineError):
    pass


class MissingExprError(CASError):
    pass


class MissingVarError(MissingExprError):
    pass


class MissingConstError(MissingExprError):
    pass