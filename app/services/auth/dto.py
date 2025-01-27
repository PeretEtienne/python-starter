from dataclasses import dataclass


@dataclass
class RegisterData():
    first_name: str
    last_name: str
    password: str
    email: str
