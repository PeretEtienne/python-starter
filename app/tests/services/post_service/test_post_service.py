
import pytest
from prisma.models import Post, User
from prisma.partials import PostWithAuthor, UserSafe
from prisma.types import PostCreateInput, PostUpdateInput
from pytest_mock import MockerFixture

from app.services.post_service.dto import PostCreateDTO, PostUpdateDTO
from app.services.post_service.errors import NotAuthorizedPatchPostError, PostNotFoundError
from app.services.post_service.post_service import PostService


@pytest.fixture
def post_service(mocker: MockerFixture) -> PostService:
    post_repo_mock = mocker.MagicMock()
    user_repo_mock = mocker.MagicMock()
    return PostService(
        post_repo=post_repo_mock,
        user_repo=user_repo_mock,
    )


@pytest.fixture
def mock_post() -> Post:
    return Post(
        id=1,
        content="",
        published=True,
        title="",
        author_id=1,
    )


@pytest.fixture
def mock_user() -> User:
    return User(
        id=1,
        email="test2@test.com",
        first_name="test",
        last_name="test",
        is_active=True,
        hashed_password="",
    )


@pytest.mark.asyncio
async def test_create_post(
    post_service: PostService,
    mocker: MockerFixture,
    mock_user: User,
) -> None:
    post_service.post_repo.create = mocker.AsyncMock()

    post_create_dto = PostCreateDTO(
        title="test",
        content="test",
        published=True,
        user_id=mock_user.id,
    )

    await post_service.create_post(mock_user.id, post_create_dto)

    post_service.post_repo.create.assert_awaited_once_with(
        PostCreateInput(
            title=post_create_dto.title,
            content=post_create_dto.content,
            published=post_create_dto.published,
            author_id=mock_user.id,
        ),
    )


@pytest.mark.asyncio
async def test_get_post(
    post_service: PostService,
    mock_post: Post,
    mocker: MockerFixture,
) -> None:
    post_id = 1

    post_service.post_repo.get_by_id = mocker.AsyncMock(return_value=mock_post)

    result = await post_service.get_post(post_id)

    assert result == mock_post
    post_service.post_repo.get_by_id.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_get_post_not_found(
    post_service: PostService,
    mocker: MockerFixture,
) -> None:
    post_id = 1

    post_service.post_repo.get_by_id = mocker.AsyncMock(return_value=None)

    with pytest.raises(PostNotFoundError):
        await post_service.get_post(post_id)

    post_service.post_repo.get_by_id.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_get_published(
    post_service: PostService, mocker: MockerFixture,
) -> None:

    mock_data = [
        PostWithAuthor(
            id=1,
            content="",
            published=True,
            title="",
            author_id=1,
            author=UserSafe(
                id=1,
                email="test@test.com",
                first_name="test",
                last_name="test",
                is_active=True,
            ),
        ),
        PostWithAuthor(
            id=2,
            content="",
            published=True,
            title="",
            author_id=2,
            author=UserSafe(
                id=2,
                email="test2@test.com",
                first_name="test",
                last_name="test",
                is_active=True,
            ),
        ),
    ]

    post_service.post_repo.get_published = mocker.AsyncMock(return_value=mock_data)

    result = await post_service.get_published()

    assert result == mock_data
    post_service.post_repo.get_published.assert_called_once()


@pytest.mark.asyncio
async def test_patch_post_success(
    post_service: PostService,
    mock_post: Post,
    mock_user: User,
    mocker: MockerFixture,
) -> None:
    post_id = 1
    post_updates = PostUpdateDTO(
        title="new title",
        content="new content",
    )

    post_service.post_repo.get_by_id = mocker.AsyncMock(return_value=mock_post)
    post_service.post_repo.patch_post = mocker.AsyncMock(return_value=mock_post)

    await post_service.patch_post(
        user=mock_user,
        post_id=post_id,
        updates_dto=post_updates,
    )

    post_service.post_repo.get_by_id.assert_awaited_once_with(
        post_id,
    )
    post_service.post_repo.patch_post.assert_awaited_once_with(
        post_id,
        PostUpdateInput(title=post_updates.title),
    )


@pytest.mark.asyncio
async def test_patch_post_not_found(
    post_service: PostService,
    mock_user: User,
    mocker: MockerFixture,
) -> None:
    post_id = 1
    post_updates = PostUpdateDTO(
        title="new title",
    )

    post_service.post_repo.get_by_id = mocker.AsyncMock(return_value=None)

    with pytest.raises(PostNotFoundError):
        await post_service.patch_post(
            mock_user,
            post_id,
            post_updates,
        )

    post_service.post_repo.get_by_id.assert_awaited_once_with(post_id)


@pytest.mark.asyncio
async def test_patch_post_not_authorized(
    post_service: PostService,
    mock_user: User,
    mocker: MockerFixture,
) -> None:
    post_id = 1
    post_updates = PostUpdateDTO(
        title="new title",
    )
    mock_post = Post(
        id=1,
        content="",
        published=True,
        title="",
        author_id=2,  # Diffrent from mock_user.id
    )

    post_service.post_repo.get_by_id = mocker.AsyncMock(return_value=mock_post)

    with pytest.raises(NotAuthorizedPatchPostError):
        await post_service.patch_post(
            mock_user,
            post_id,
            post_updates,
        )

    post_service.post_repo.get_by_id.assert_awaited_once_with(post_id)
