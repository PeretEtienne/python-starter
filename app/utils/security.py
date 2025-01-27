from argon2 import PasswordHasher


def hash_password(password: str) -> str:
    return PasswordHasher().hash(password)
