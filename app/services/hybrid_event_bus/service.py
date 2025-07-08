import asyncio
from collections import defaultdict
from enum import StrEnum
from typing import Any, Awaitable, Callable, Type

from app.services.logger.service import Logger


class EventHandlerMode(StrEnum):
    BLOCKING = "blocking"
    ASYNC = "async"

class HybridEventBus():
    def __init__(self) -> None:
        self._blocking_handlers: dict[Type, list[Callable[[Any], Awaitable[None]]]] = defaultdict(list)
        self._async_handlers: dict[Type, list[Callable[[Any], Awaitable[None]]]] = defaultdict(list)

    def subscribe(
        self,
        event_type: Type,
        handler: Callable[[Any], Awaitable[None]],
        mode: EventHandlerMode = EventHandlerMode.BLOCKING,
    ) -> None:
        if mode == EventHandlerMode.BLOCKING:
            self._blocking_handlers[event_type].append(handler)
        elif mode == EventHandlerMode.ASYNC:
            self._async_handlers[event_type].append(handler)

    async def publish(self, event: Any) -> None:
        event_type = type(event)

        blocking_tasks = [handler(event) for handler in self._blocking_handlers[event_type]]
        if blocking_tasks:
            await asyncio.gather(*blocking_tasks)

        for handler in self._async_handlers[event_type]:
            # We deliberately fire and forget async handlers - no await or task tracking needed
            asyncio.create_task(self._safe_run(handler, event))  # noqa: RUF006

    async def _safe_run(self, handler: Callable[[Any], Awaitable[None]], event: Any) -> None:
        try:
            await handler(event)
        except Exception as e:
            Logger.error(f"[HybridEventBus] handler {handler.__name__} failed: {e}")

event_bus = HybridEventBus()
