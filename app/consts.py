from enum import StrEnum


class Permission(StrEnum):

    ADMINISTRATE = "administrate"
    IMPERSONATE = "impersonate"
    CREATE_USER = "create_user"


class EventLogType(StrEnum):
    pass
