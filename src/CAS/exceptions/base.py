class CASError(Exception):
    pass


class InvalidSubroutineError(CASError):
    pass


class MissingVariableError(CASError):
    pass