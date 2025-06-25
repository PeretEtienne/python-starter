from typing import Annotated, Callable, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.exceptions import UserNotExists

from app.auth.auth_backend import (
    AuthenticationBackendRefresh,
    BearerTransportRefresh,
)
from app.auth.auth_token import get_jwt_strategy, get_refresh_jwt_strategy
from app.consts import Permission
from app.db.dao.user_manager_dao import UserManager, get_user_manager
from app.db.models.user_model import User


def has_permission(user: User, permission: Permission) -> bool:
    return permission in user.permissions


def can(permission: Permission) -> Callable[[User], User]:
    def checker(user: User = Depends(current_active_user)) -> User:
        if not has_permission(user, permission) and not has_permission(
            user,
            Permission.ADMINISTRATE,
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user

    return checker


bearer_transport_refresh = BearerTransportRefresh(tokenUrl="auth/login")

auth_backend_refresh = AuthenticationBackendRefresh(
    name="jwt",
    transport=bearer_transport_refresh,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend_refresh])


async def current_active_user(
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    x_impersonate: Annotated[Optional[str], Header()] = None,
    user_dao: UserManager = Depends(get_user_manager),
) -> User:
    if x_impersonate and has_permission(current_user, Permission.IMPERSONATE):
        try:
            to_impersonate = await user_dao.get_by_email(x_impersonate)
        except UserNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
        return to_impersonate
    return current_user
