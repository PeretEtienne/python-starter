

from app.db.dao.user_dao import UserDAO
from app.services.logger.service import Logger
from app.services.post.events import PostCreatedEvent


async def send_email(*, event: PostCreatedEvent, user_dao: UserDAO) -> None:
    author = await user_dao.get_by_id(event.author_id)

    if author is None:
        Logger.error(f"[EMAIL] Author with ID {event.author_id} not found for email notification.")
        return

    Logger.info(f"[EMAIL] Sending email to author {author.email} for post creation.")
