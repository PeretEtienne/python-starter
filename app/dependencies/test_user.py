from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from prisma.models import User
from pytest_mock.plugin import MockerFixture

from app.dependencies.user import get_current_user


@pytest.fixture
def mock_db(mocker: MockerFixture):
    db = mocker.Mock()
    db.user.find_first = AsyncMock()
    mocker.patch("app.dependencies.db.get_db_session", return_value=db)
    return db


@pytest.fixture
def mock_decode_token(mocker: MockerFixture):
    return mocker.patch("app.dependencies.user.decode_token")


@pytest.mark.asyncio
async def test_get_current_user_valid(mock_db: MockerFixture, mock_decode_token: MockerFixture):
    user_id = 1
    mock_decode_token.return_value = {
        "sub": str(user_id),
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp(),
    }

    mock_db.user.find_first.return_value = User(
        id=user_id,
        email="test@example.com",
        hashed_password="hashed_password",
        refresh_token="other_refresh_token",
        first_name="John",
        last_name="Doe",
        is_active=True,
    )

    user = await get_current_user("valid_token", mock_db)

    assert user.id == 1
    assert user.email == "test@example.com"
    mock_db.user.find_first.assert_called_once_with(
        where={"id": user_id, "is_active": True},
    )


@pytest.mark.asyncio
async def test_get_current_user_token_expired(mock_db: MockerFixture, mock_decode_token: MockerFixture):
    mock_decode_token.return_value = {
        "sub": "1",
        "exp": (datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp(),
    }

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("expired_token", mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db: MockerFixture, mock_decode_token: MockerFixture):
    mock_decode_token.return_value = {"exp": (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_db: MockerFixture, mock_decode_token: MockerFixture):
    mock_decode_token.return_value = {
        "sub": "1",
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp(),
    }

    mock_db.user.find_first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("valid_token", mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_current_user_unexpected_error(mock_db: MockerFixture, mock_decode_token: MockerFixture):
    mock_decode_token.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception) as exc_info:
        await get_current_user("valid_token", mock_db)

    assert str(exc_info.value) == "Unexpected error"
