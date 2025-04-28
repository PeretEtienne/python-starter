from dataclasses import dataclass


@dataclass
class TokensDTO():
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
