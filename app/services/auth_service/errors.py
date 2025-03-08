class UserAlreadyExistsError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
