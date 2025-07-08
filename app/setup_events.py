from app.db.dao.user_dao import UserDAO
from app.db.session_manager import session_manager
from app.services.hybrid_event_bus.service import EventHandlerMode, HybridEventBus
from app.services.post.event_handlers import send_email
from app.services.post.events import PostCreatedEvent


def register_event_handlers(bus: HybridEventBus) -> None:
    bus.subscribe(PostCreatedEvent, post_creation_email_wrapper, mode=EventHandlerMode.ASYNC)

async def post_creation_email_wrapper(event: PostCreatedEvent) -> None:
    async with session_manager.context() as db_session:
        user_dao = UserDAO(db_session)
        await send_email(event=event, user_dao=user_dao)
