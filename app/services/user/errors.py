from enum import StrEnum


class ChangePasswordError(StrEnum):

    INVALID_OLD_PASSWORD = "INVALID_OLD_PASSWORD"
    INVALID_NEW_PASSWORD = "INVALID_NEW_PASSWORD"
