from unittest.mock import patch

import pytest

from app.services.logger.service import Logger, LogLevel
from app.settings import settings


@pytest.fixture
def default_exc_info() -> bool:
    return settings.exc_info


@pytest.fixture
def default_stack_info() -> bool:
    return settings.stack_info


@pytest.fixture
def default_stacklevel() -> int:
    return settings.stacklevel


@pytest.mark.parametrize(
    "log_method, level_enum",
    [
        ("log", LogLevel.DEBUG),
        ("info", LogLevel.INFO),
        ("warning", LogLevel.WARNING),
        ("error", LogLevel.ERROR),
    ],
)
def test_logger_methods_call_standard_logger(
    log_method: str,
    level_enum: LogLevel,
    default_exc_info: bool,
    default_stack_info: bool,
    default_stacklevel: int,
) -> None:
    msg = "Test log message"
    exc_info = default_exc_info
    stack_info = default_stack_info
    stacklevel = default_stacklevel

    with patch("app.services.logger.service.logger.log") as mock_std_logger:
        if log_method == "log":
            Logger.log(
                level=level_enum,
                msg=msg,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel,
            )
        else:
            method = getattr(Logger, log_method)
            method(
                msg=msg,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel,
            )

        mock_std_logger.assert_called_once_with(
            level=level_enum.value,
            msg=msg,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )


@pytest.mark.parametrize(
    "custom_exc_info, custom_stack_info, custom_stacklevel",
    [
        (True, True, 5),
        (False, False, 2),
    ],
)
def test_logger_with_custom_params_calls_standard_logger(
    custom_exc_info: bool,
    custom_stack_info: bool,
    custom_stacklevel: int,
) -> None:
    msg = "Custom params test"

    with patch("app.services.logger.service.logger.log") as mock_std_logger:
        Logger.info(
            msg=msg,
            exc_info=custom_exc_info,
            stack_info=custom_stack_info,
            stacklevel=custom_stacklevel,
        )

        mock_std_logger.assert_called_once_with(
            level=LogLevel.INFO.value,
            msg=msg,
            exc_info=custom_exc_info,
            stack_info=custom_stack_info,
            stacklevel=custom_stacklevel,
        )

