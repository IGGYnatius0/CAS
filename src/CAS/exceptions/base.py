__all__ = ['BadMethodError', 'BadFunctionError', 'MissingVariableError']


class CASError(Exception):
    pass


class BadSubroutineError(CASError):
    pass


class BadMethodError(BadSubroutineError):
    pass


class BadFunctionError(BadSubroutineError):
    pass


class MissingVariableError(CASError):
    pass