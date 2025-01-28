class UserAlreadyExists(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


class TokenExpired(Exception):
    pass


class InvalidCredentials(Exception):
    pass
