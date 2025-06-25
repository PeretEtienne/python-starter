from typing import Callable as DependencyCallable

from fastapi.responses import JSONResponse
from fastapi_users import models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
)
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport.base import Transport
from pydantic import BaseModel

from app.settings import settings


class BearerResponseRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    async def get_login_response(self, token: str, refresh_token: str) -> JSONResponse:
        bearer_response = BearerResponseRefresh(
            access_token=token,
            refresh_token=refresh_token,
            token_type=settings.auth_token_type,
        )
        return JSONResponse(bearer_response.model_dump())


class BearerTransportRefresh(BearerTransport):

    async def get_login_response(self, token: str, refresh_token: str) -> JSONResponse:  # type: ignore
        bearer_response = BearerResponseRefresh(
            access_token=token,
            refresh_token=refresh_token,
            token_type=settings.auth_token_type,
        )
        return JSONResponse(bearer_response.model_dump())


class AuthenticationBackendRefresh(AuthenticationBackend[models.UP, models.ID]):

    def __init__(
        self,
        name: str,
        transport: Transport,
        get_strategy: DependencyCallable[[], Strategy[models.UP, models.ID]],
        get_refresh_strategy: DependencyCallable[[], Strategy[models.UP, models.ID]],
    ) -> None:
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UP,
    ) -> JSONResponse:
        token = await strategy.write_token(user)
        refresh_strategy = self.get_refresh_strategy()
        refresh_token = await refresh_strategy.write_token(user)
        return await self.transport.get_login_response(
            token=token,
            refresh_token=refresh_token,  # type: ignore
        )
