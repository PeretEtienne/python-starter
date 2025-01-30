import pytest
from app.services.auth.auth_service import AuthService
from app.services.auth.dto import RegisterData, Tokens
from app.services.auth.errors import InvalidCredentials, TokenExpired, UserAlreadyExists
from prisma.models import User

from app.utils.security import verify_password


@pytest.fixture
def auth_service(mocker):
    user_repo_mock = mocker.MagicMock()
    return AuthService(user_repo_mock)


@pytest.mark.asyncio
async def test_register_user_success(auth_service, mocker):
    register_data = RegisterData(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="hashed_password"
    )

    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=None)
    auth_service.user_repo.create_user = mocker.AsyncMock(return_value=User(
        id=1,
        email=register_data.email,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        hashed_password="hashed_password",
        is_active=True
    ))

    user = await auth_service.register(register_data)

    auth_service.user_repo.get_user_by_email.assert_awaited_once_with(register_data.email)
    auth_service.user_repo.create_user.assert_awaited_once()

    assert user.email == register_data.email
    assert user.first_name == register_data.first_name
    assert user.last_name == register_data.last_name


@pytest.mark.asyncio
async def test_register_user_already_exists(auth_service, mocker):
    register_data = RegisterData(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="hashed_password"
    )

    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=User(
        id=1,
        email=register_data.email,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        hashed_password="hashed_password",
        is_active=True
    ))

    with pytest.raises(UserAlreadyExists):
        await auth_service.register(register_data)


@pytest.mark.asyncio
async def test_register_user_unexpected_error(auth_service, mocker):
    register_data = RegisterData(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="hashed_password"
    )

    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(Exception):
        await auth_service.register(register_data)


@pytest.mark.asyncio
async def test_login_success(auth_service, mocker):
    email = "test@example.com"
    password = "correct_password"
    hashed_password = "hashed_password"

    mocker.patch("app.services.auth.auth_service.verify_password", return_value=True)

    user = User(
        id=1,
        email=email,
        hashed_password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=user)
    auth_service.user_repo.update_user_refresh_token = mocker.AsyncMock()

    mocker.patch(
        "app.services.auth.auth_service.create_access_token",
        side_effect=lambda data, expires_delta: f"token_{data['sub']}"
    )
    expected_token = f"token_{user.id}"

    tokens = await auth_service.login(email, password)

    auth_service.user_repo.get_user_by_email.assert_awaited_once_with(email)
    auth_service.user_repo.update_user_refresh_token.assert_awaited_once_with(user.id, expected_token)
    assert isinstance(tokens, Tokens)
    assert tokens.access_token == expected_token
    assert tokens.refresh_token == expected_token


@pytest.mark.asyncio
async def test_login_invalid_email(auth_service, mocker):
    email = "invalid@example.com"
    password = "some_password"

    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials, match="Invalid credentials"):
        await auth_service.login(email, password)

    auth_service.user_repo.get_user_by_email.assert_awaited_once_with(email)


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, mocker):
    email = "test@example.com"
    password = "wrong_password"
    hashed_password = "hashed_password"

    mocker.patch("app.services.auth.auth_service.verify_password", return_value=False)

    user = User(
        id=1,
        email=email,
        hashed_password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=user)

    with pytest.raises(InvalidCredentials, match="Invalid credentials"):
        await auth_service.login(email, password)

    auth_service.user_repo.get_user_by_email.assert_awaited_once_with(email)


@pytest.mark.asyncio
async def test_login_update_refresh_token_failed(auth_service, mocker):
    email = "test@example.com"
    password = "correct_password"
    hashed_password = "hashed_password"

    mocker.patch("app.services.auth.auth_service.verify_password", return_value=True)

    user = User(
        id=1,
        email=email,
        hashed_password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get_user_by_email = mocker.AsyncMock(return_value=user)
    auth_service.user_repo.update_user_refresh_token = mocker.AsyncMock(
        side_effect=Exception("Database error")
    )

    mocker.patch(
        "app.services.auth.auth_service.create_access_token",
        side_effect=lambda data, expires_delta: f"token_{data['sub']}"
    )
    expected_token = f"token_{user.id}"

    with pytest.raises(Exception, match="Database error"):
        await auth_service.login(email, password)

    auth_service.user_repo.get_user_by_email.assert_awaited_once_with(email)
    auth_service.user_repo.update_user_refresh_token.assert_awaited_once_with(
        user.id, expected_token
    )


@pytest.mark.asyncio
async def test_refresh_success(auth_service, mocker):
    user_id = 1
    old_refresh_token = "valid_refresh_token"
    new_access_token = "new_access_token"
    new_refresh_token = "new_refresh_token"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": str(user_id), "exp": 9999999999}
    )

    mocker.patch(
        "app.services.auth.auth_service.create_access_token",
        side_effect=[new_access_token, new_refresh_token]
    )

    user = User(
        id=user_id,
        email="email",
        hashed_password="hashed_password",
        refresh_token=old_refresh_token,
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get = mocker.AsyncMock(
        return_value=user
    )

    auth_service.user_repo.update_user_refresh_token = mocker.AsyncMock()

    tokens = await auth_service.refresh(old_refresh_token)

    assert tokens.access_token == new_access_token
    assert tokens.refresh_token == new_refresh_token
    auth_service.user_repo.update_user_refresh_token.assert_called_once_with(
        user_id, new_refresh_token
    )


@pytest.mark.asyncio
async def test_refresh_invalid_token(auth_service, mocker):
    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        side_effect=Exception("Invalid token")
    )

    with pytest.raises(InvalidCredentials, match="Invalid refresh token"):
        await auth_service.refresh("invalid_token")


@pytest.mark.asyncio
async def test_refresh_user_not_found(auth_service, mocker):
    valid_token = "valid_refresh_token"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 9999999999}
    )

    auth_service.user_repo.get = mocker.AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials, match="Invalid refresh token"):
        await auth_service.refresh(valid_token)


@pytest.mark.asyncio
async def test_refresh_token_expired(auth_service, mocker):
    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 0}
    )

    with pytest.raises(TokenExpired, match="Token has expired"):
        await auth_service.refresh("token")


@pytest.mark.asyncio
async def test_refresh_token_mismatch(auth_service, mocker):
    user_id = 1
    invalid_refresh_token = "invalid_refresh_token"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": str(user_id), "exp": 9999999999}
    )

    user = User(
        id=user_id,
        email="email",
        hashed_password="hashed_password",
        refresh_token="other_refresh_token",
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get = mocker.AsyncMock(return_value=user)

    with pytest.raises(InvalidCredentials, match="Invalid refresh token"):
        await auth_service.refresh(invalid_refresh_token)


@pytest.mark.asyncio
async def test_reset_password_success(auth_service, mocker):
    reset_token = "valid_reset_token"
    new_password = "new_password"
    user_id = 1

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 9999999999}
    )

    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="old_hashed_password",
        reset_token=reset_token,
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get = mocker.AsyncMock(return_value=user)

    auth_service.user_repo.update_user_password = mocker.AsyncMock()
    auth_service.user_repo.update_user_reset_token = mocker.AsyncMock()

    await auth_service.reset_password(reset_token, new_password)

    auth_service.user_repo.get.assert_awaited_once_with(user_id)

    auth_service.user_repo.update_user_password.assert_awaited_once_with(user_id, mocker.ANY)
    args, _ = auth_service.user_repo.update_user_password.await_args
    hashed_password = args[1]

    assert verify_password(hashed_password, new_password)
    auth_service.user_repo.update_user_reset_token.assert_awaited_once_with(user_id, None)


@pytest.mark.asyncio
async def test_reset_password_invalid_token(auth_service, mocker):
    reset_token = "invalid_reset_token"
    new_password = "new_password"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        side_effect=Exception("Invalid token")
    )

    with pytest.raises(InvalidCredentials, match="Invalid reset token"):
        await auth_service.reset_password(reset_token, new_password)


@pytest.mark.asyncio
async def test_reset_password_token_expired(auth_service, mocker):
    reset_token = "expired_reset_token"
    new_password = "new_password"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 0}  # Token expired
    )

    with pytest.raises(TokenExpired, match="Token has expired"):
        await auth_service.reset_password(reset_token, new_password)


@pytest.mark.asyncio
async def test_reset_password_user_not_found(auth_service, mocker):
    reset_token = "valid_reset_token"
    new_password = "new_password"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 9999999999}
    )

    auth_service.user_repo.get = mocker.AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials, match="Invalid reset token"):
        await auth_service.reset_password(reset_token, new_password)


@pytest.mark.asyncio
async def test_reset_password_token_mismatch(auth_service, mocker):
    reset_token = "valid_reset_token"
    new_password = "new_password"

    mocker.patch(
        "app.services.auth.auth_service.decode_token",
        return_value={"sub": "1", "exp": 9999999999}
    )

    user = User(
        id=1,
        email="test@example.com",
        hashed_password="old_hashed_password",
        reset_token="different_reset_token",
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    auth_service.user_repo.get = mocker.AsyncMock(return_value=user)

    with pytest.raises(InvalidCredentials, match="Invalid reset token"):
        await auth_service.reset_password(reset_token, new_password)
