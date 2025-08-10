from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from contextvars import ContextVar


session_ctx: ContextVar = ContextVar("session_ctx")

class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str,Any]],Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str,Any]
    ) -> Any:
        print(">> DataBaseSession работает")
        async with self.session_pool() as session:
            token = session_ctx.set(session)
            data['session'] = session
            try:
                return await handler(event, data)
            finally:
                session_ctx.reset(token)