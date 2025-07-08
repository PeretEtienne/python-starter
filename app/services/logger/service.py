import logging
from enum import Enum

from app.settings import settings


class LogLevel(Enum):

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


logger = logging.getLogger(settings.logger_name)


class Logger:

    @staticmethod
    def log(
        level: LogLevel,
        msg: object,
        exc_info: bool = settings.exc_info,
        stack_info: bool = settings.stack_info,
        stacklevel: int = settings.stacklevel,
    ) -> None:
        logger.log(
            level=level.value,
            msg=msg,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    @staticmethod
    def info(
        msg: object,
    ) -> None:
        Logger.log(
            level=LogLevel.INFO,
            msg=msg,
            exc_info=False,
            stack_info=False,
            stacklevel=False,
        )

    @staticmethod
    def warning(
        msg: object,
        exc_info: bool = settings.exc_info,
        stack_info: bool = settings.stack_info,
        stacklevel: int = settings.stacklevel,
    ) -> None:
        Logger.log(
            level=LogLevel.WARNING,
            msg=msg,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    @staticmethod
    def error(
        msg: object,
        exc_info: bool = settings.exc_info,
        stack_info: bool = settings.stack_info,
        stacklevel: int = settings.stacklevel,
    ) -> None:
        Logger.log(
            level=LogLevel.ERROR,
            msg=msg,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )
