import pytest
from app.services.auth.auth_service import AuthService
from app.services.auth.dto import RegisterData
from app.services.auth.errors import UserAlreadyExists
from prisma.models import User


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
