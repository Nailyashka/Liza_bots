import asyncio
import logging
import os


from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.client.bot import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from config import settings_bot
from db.helper_db import create_db, delete_db, session_maker
from handlers.user import user_menu
# from admin.admin_main import admin
from middlewares.db import DataBaseSession
# from admin.routers.car_routers_admin import admin_cars_router
# from config import settings_redis




if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s-%(name)s-%(message)s')

async def main():
    bot = Bot(token=settings_bot.TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # redis_client = aioredis.from_url(settings_redis.REDIS_URL)
    # storage=RedisStorage(redis_client)
    dp = Dispatcher()
    
    dp.include_router(user_menu)
    logging.debug("Роутеры подключены")
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    # dp.update.middleware(UserMiddleware(session_maker=session_maker))
    
    dp.startup.register(on_start_up)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
    
async def on_start_up():
    await create_db()
    # await delete_db()
    
     
async def shut_down():
    await delete_db()
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот выключён')