import hashlib
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager
from fastapi_users.db import SQLAlchemyUserDatabase

from app.auth.auth_token import generate_token
from app.db.models.user_model import User
from app.dependencies.db import get_user_db
from app.services.email.dto import EmailMessageData
from app.services.email.service import EmailService
from app.settings import settings

SECRET = settings.auth_secret
RESET_LIFETIME_SECONDS = settings.auth_reset_seconds

logger = logging.getLogger(settings.logger_name)


class UserManager(BaseUserManager[User, int]):

    reset_password_token_secret = SECRET
    reset_password_token_lifetime_seconds = RESET_LIFETIME_SECONDS

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        logger.info(f"User {user.email} registered.")

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        receivers = [user.email]

        logger.info(f"User {user.email} forgot password.")
        logger.debug(f"Reset password token: {token}")

        EmailService().send(
            EmailMessageData(
                receivers=receivers,
                subject="Reset password",
                data={
                    "user": f"{user.first_name} {user.last_name}",
                    "url": f"{settings.frontend_url}/reset-password?reset_token={token}&email={user.email}",
                    "reset_mail_link_expiracy": settings.reset_mail_link_expiracy,
                },
                tpl="reset_password",
            ),
        )

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        refresh_token = generate_token(user.id, refresh=True)
        hasher = hashlib.sha3_256()
        hasher.update(refresh_token.encode())
        user.refresh_token = hasher.hexdigest()
        user.last_login = datetime.now()
        logger.info(f"User {user.email} logged in.")

    async def on_after_logout(self, user: User, response: Response) -> None:
        user.refresh_token = ""
        logger.info(f"User {user.email} logged out.")

    def parse_id(self, value: Any) -> int:
        return int(value)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[Any, Any]:
    yield UserManager(user_db)
