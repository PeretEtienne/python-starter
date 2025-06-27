from enum import StrEnum
from http import HTTPStatus
from typing import TypedDict


class ErrorDetail(TypedDict):

    code: str
    message: str


class HttpExceptionArgs(TypedDict):

    status_code: int
    detail: ErrorDetail


class DomainError(Exception):

    def __init__(
        self,
        *,
        detail: ErrorDetail,
        status_code: int = HTTPStatus.BAD_REQUEST,
    ) -> None:
        self.detail = detail
        self.status_code = status_code

    def to_http_args(self) -> HttpExceptionArgs:
        return {"detail": self.detail, "status_code": self.status_code}


class ChangePasswordError(StrEnum):

    INVALID_OLD_PASSWORD = "invalid_old_password"
    INVALID_NEW_PASSWORD = "invalid_new_password"
