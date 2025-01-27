from dataclasses import dataclass


@dataclass
class RegisterData():
    first_name: str
    last_name: str
    password: str
    email: str


@dataclass
class Tokens():
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
