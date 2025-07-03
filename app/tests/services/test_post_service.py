from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from app.db.dao.post_dao import DAOPostCreateDTO
from app.db.models.user_model import User
from app.errors import CreatePostError, DomainError
from app.services.post.dto import PostCreateDTO
from app.services.post.service import PostService


@pytest.fixture
def post_service(mocker: MockerFixture) -> PostService:
    mock_post_dao = mocker.MagicMock()
    mock_user_dao = mocker.MagicMock()
    return PostService(post_dao=mock_post_dao, user_dao=mock_user_dao)

@pytest.fixture
def author() -> User:
    return User(
        id=1,
        email="test@example.com",
        hashed_password="fakehashedpassword",
        first_name="John",
        last_name="Doe",
        permissions=[],  # adapte selon ton Enum
        refresh_token=None,
        last_login=datetime(2024, 1, 1, 10, 0, 0),
        is_active=True,
        created_by=None,
        updated_by=None,
        created_at=datetime(2024, 1, 1, 9, 0, 0),
        updated_at=datetime(2024, 1, 2, 9, 0, 0),
    )


@pytest.mark.asyncio
async def test_create_post_success(
    post_service: PostService,
    mocker: MockerFixture,
    author: User,
) -> None:
    expected_post_id = 123
    post_service.user_dao.get_by_id = cast(AsyncMock, mocker.AsyncMock(return_value=author))
    post_service.post_dao.create = cast(AsyncMock, mocker.AsyncMock(return_value=expected_post_id))

    data = PostCreateDTO(
        title="A valid title",
        content="Some valid content",
        published=True,
        author_id=2,
        created_by=2,
    )

    post_id = await post_service.create_post(data=data)

    assert post_id == expected_post_id
    post_service.post_dao.create.assert_awaited_once()
    args, _ = post_service.post_dao.create.call_args
    dto_passed = args[0]
    assert isinstance(dto_passed, DAOPostCreateDTO)
    assert dto_passed.title == data.title
    assert dto_passed.content == data.content
    assert dto_passed.published == data.published
    assert dto_passed.author_id == data.author_id
    assert dto_passed.created_by == data.created_by


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_data, expected_message_part",
    [
        (
            PostCreateDTO(
                title="DRAFT - forbidden title",
                content="Valid content",
                published=True,
                author_id=2,
                created_by=2,
            ),
            "title cannot start with 'DRAFT -'",
        ),
        (
            PostCreateDTO(
                title="A valid title",
                content="Some valid content",
                published=True,
                author_id=1,
                created_by=1,
            ),
            "author id must be even",
        ),
    ],
)
async def test_create_post_invalid_data(
    post_service: PostService,
    invalid_data: PostCreateDTO,
    expected_message_part: str,
) -> None:
    with pytest.raises(DomainError) as exc_info:
        await post_service.create_post(data=invalid_data)

    err = exc_info.value
    assert expected_message_part.lower() in err.detail["message"].lower()


@pytest.mark.asyncio
async def test_create_post_with_non_existent_author(
    post_service: PostService,
    mocker: MockerFixture,
) -> None:
    post_service.user_dao.get_by_id = cast(AsyncMock, mocker.AsyncMock(return_value=None))

    data = PostCreateDTO(
        title="A valid title",
        content="Some valid content",
        published=True,
        author_id=2,
        created_by=2,
    )

    with pytest.raises(DomainError) as exc_info:
        await post_service.create_post(data=data)

    err = exc_info.value
    assert err.detail["code"] == CreatePostError.AUTHOR_NOT_FOUND
    assert "Author not found." in err.detail["message"]
