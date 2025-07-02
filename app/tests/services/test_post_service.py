import pytest
from pytest_mock import MockerFixture

from app.db.dao.post_dao import DAOPostCreateDTO
from app.errors import CreatePostError, DomainError
from app.services.post.dto import PostCreateDTO
from app.services.post.service import PostService


@pytest.fixture
def post_service(mocker: MockerFixture) -> PostService:
    mock_post_dao = mocker.MagicMock()
    return PostService(post_dao=mock_post_dao)


@pytest.mark.asyncio
async def test_create_post_success(
    post_service: PostService,
    mocker: MockerFixture,
) -> None:
    expected_post_id = 123
    post_service.post_dao.create = mocker.AsyncMock(return_value=expected_post_id)

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
    "invalid_data, expected_code, expected_message_part",
    [
        (
            PostCreateDTO(
                title="DRAFT - forbidden title",
                content="Valid content",
                published=True,
                author_id=2,
                created_by=2,
            ),
            CreatePostError.INVALID_DATA,
            "validation failed",
        ),
        (
            PostCreateDTO(
                title="A valid title",
                content="Some valid content",
                published=True,
                author_id=1,
                created_by=1,
            ),
            CreatePostError.INVALID_AUTHOR_ID,
            "author id must be even",
        ),
    ],
)
async def test_create_post_invalid_cases(
    post_service: PostService,
    invalid_data: PostCreateDTO,
    expected_code: str,
    expected_message_part: str,
) -> None:
    with pytest.raises(DomainError) as exc_info:
        await post_service.create_post(data=invalid_data)

    err = exc_info.value
    assert err.detail["code"] == expected_code
    assert expected_message_part.lower() in err.detail["message"].lower()
