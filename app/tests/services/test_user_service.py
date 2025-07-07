from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from app.db.models.user_model import User
from app.errors import DomainError
from app.services.user.errors import ChangePasswordError
from app.services.user.schemas import ValidatePasswordSchema
from app.services.user.service import UserService


@pytest.fixture
def user_service(mocker: MockerFixture) -> UserService:
    mock_user_dao = mocker.MagicMock()
    return UserService(user_dao=mock_user_dao)


@pytest.mark.asyncio
async def test_change_password_success(
    user_service: UserService,
    mocker: MockerFixture,
) -> None:
    user_id = 1
    hashed_password = "old_hash"
    old_password = "correct_password"
    new_password = "Valid1@Password"

    user = User(id=user_id, hashed_password=hashed_password)

    mock_hasher = mocker.MagicMock()
    mock_hasher.verify.return_value = True
    mocker.patch("app.services.user.service.PasswordHasher", return_value=mock_hasher)

    user_service.user_dao.patch_password = AsyncMock()

    await user_service.change_password(
        user=user,
        old_password=old_password,
        new_password=new_password,
    )

    mock_hasher.verify.assert_called_once_with(hashed_password, old_password)
    user_service.user_dao.patch_password.assert_awaited_once_with(
        user_id=user_id,
        password=new_password,
    )


@pytest.mark.asyncio
async def test_change_password_wrong_old_password(
    user_service: UserService,
    mocker: MockerFixture,
) -> None:
    user_id = 1
    hashed_password = "stored_hash"
    wrong_password = "wrong_password"
    new_password = "Valid1@Password"

    user = User(id=user_id, hashed_password=hashed_password)

    mock_hasher = mocker.MagicMock()
    mock_hasher.verify.side_effect = Exception("Invalid password")
    mocker.patch("app.services.user.service.PasswordHasher", return_value=mock_hasher)

    with pytest.raises(DomainError) as exc_info:
        await user_service.change_password(
            user=user,
            old_password=wrong_password,
            new_password=new_password,
        )

    err = exc_info.value
    assert err.detail["code"] == ChangePasswordError.INVALID_OLD_PASSWORD
    mock_hasher.verify.assert_called_once_with(hashed_password, wrong_password)


@pytest.mark.asyncio
async def test_change_password_invalid_new_password(
    user_service: UserService,
    mocker: MockerFixture,
) -> None:
    user_id = 1
    hashed_password = "stored_hash"
    old_password = "correct_password"
    invalid_new_password = "NoDigit@Pass"

    user = User(id=user_id, hashed_password=hashed_password)

    mock_hasher = mocker.MagicMock()
    mock_hasher.verify.return_value = True
    mocker.patch("app.services.user.service.PasswordHasher", return_value=mock_hasher)

    with pytest.raises(DomainError) as exc_info:
        await user_service.change_password(
            user=user,
            old_password=old_password,
            new_password=invalid_new_password,
        )

    err = exc_info.value
    assert err.detail["code"] == ChangePasswordError.INVALID_NEW_PASSWORD
    mock_hasher.verify.assert_called_once_with(hashed_password, old_password)


def test_valid_password_schema() -> None:
    schema = ValidatePasswordSchema(password="Valid1@Password")
    assert schema.password == "Valid1@Password"


@pytest.mark.parametrize(
    "password, expected_error",
    [
        ("short1@", "String should have at least 8 characters"),
        ("1111111@", "Password must contain at least one letter"),
        ("nouppercase1@", "Password must contain at least one uppercase letter"),
        ("NOLOWERCASE1@", "Password must contain at least one lowercase letter"),
        ("NoDigit@", "Password must contain at least one digit"),
        ("NoSpecial1", "Password must contain at least one special character"),
        ("A" * 129 + "1@", "String should have at most 128 characters"),
    ],
)
def test_invalid_password_schema(password: str, expected_error: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        ValidatePasswordSchema(password=password)
    assert expected_error in str(exc_info.value)
