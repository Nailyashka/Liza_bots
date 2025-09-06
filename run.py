import asyncio
import logging
import os

from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.client.bot import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from config import settings_bot, settings_redis
from db.helper_db import create_db, delete_db, session_maker
from handlers.user import user_menu
from middlewares.user import UserMiddleware
from routers.admin import main_admin
from middlewares.db import DataBaseSession


# Для Windows
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# -------------- Меньше логов (по умолчанию) --------------
# По умолчанию — только WARNING и выше. Если нужно больше — см. ниже.
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Подавляем детализованные логи SQLAlchemy (они часто очень шумные)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
# (опционально) понижаем verbose aiogram, если нужно:
logging.getLogger("aiogram").setLevel(logging.WARNING)


async def main():
    bot = Bot(
        token=settings_bot.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Redis (FSM storage)
    redis_client = aioredis.from_url(
        settings_redis.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    storage = RedisStorage(redis_client)

    # Передаём storage в Dispatcher — важно!
    dp = Dispatcher(storage=storage)

    # Роутеры
    dp.include_routers(user_menu, main_admin)

    # Мидлвари
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.update.middleware(UserMiddleware(session_maker=session_maker))

    # Стартап
    dp.startup.register(on_start_up)

    try:
        await dp.start_polling(bot)
    finally:
        # Корректно закрываем соединения
        await bot.session.close()
        # Закрываем redis client
        await redis_client.close()


async def on_start_up():
    await create_db()
    # await delete_db()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот выключён')
