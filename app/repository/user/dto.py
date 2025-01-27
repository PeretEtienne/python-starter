from dataclasses import dataclass


@dataclass
class CreateUserDTO():
    email: str
    first_name: str
    last_name: str
    hashed_password: str
