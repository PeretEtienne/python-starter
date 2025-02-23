from dataclasses import dataclass


@dataclass
class CreateUserDBDTO():
    email: str
    first_name: str
    last_name: str
    hashed_password: str
