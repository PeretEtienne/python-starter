from dataclasses import dataclass


@dataclass
class RegisterUserInputDTO():
    first_name: str
    last_name: str
    password: str
    email: str


@dataclass
class TokensDTO():
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
