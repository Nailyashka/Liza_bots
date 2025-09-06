from aiogram.types import Message, TelegramObject, Update
from aiogram import BaseMiddleware
from sqlalchemy import select

from models.enums_model import UserRole
from models.users_model import User
from config import admins_bot


class UserMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(self, handler, event: TelegramObject, data: dict):
        print(">> MIDDLEWARE СРАБОТАЛА")
        print(f">> event: {event!r}")
        print(f">> type: {type(event)}")

        if isinstance(event, Update) and event.message and isinstance(event.message, Message):
            msg = event.message
            print(f">> message.text: {msg.text!r}")

            if msg.text and msg.text.startswith("/start"):
                session = data.get("session")
                print(">> СЕССИЯ:", session)

                if not session:
                    print(">> СЕССИИ НЕТ — ВЫХОД")
                    return await handler(event, data)

                try:
                    result = await session.execute(
                        select(User).where(User.tg_id == msg.from_user.id)
                    )
                    user = result.scalars().first()
                    print(">> НАЙДЕННЫЙ ЮЗЕР:", user)

                    if not user:
                        print(">> ДОБАВЛЯЕМ НОВОГО ЮЗЕРА")
                        role = UserRole.superadmin if msg.from_user.id in admins_bot.SUPER_ADMINS else UserRole.user
                        # code = generate_invite_code()
                        # print(f">> Сгенерирован invite_code: {code}")
                        new_user = User(
                            tg_id=msg.from_user.id,
                            username=msg.from_user.username,
                            full_name=msg.from_user.full_name,
                            role=role
                        )

                        session.add(new_user)
                        await session.commit()
                        print(f">> ЮЗЕР ДОБАВЛЕН С РОЛЬЮ {role}")
                    else:
                        print(">> ЮЗЕР УЖЕ ЕСТЬ")
                except Exception as e:
                    import traceback
                    print(">> ОШИБКА ПРИ РАБОТЕ С БАЗОЙ:", e)
                    traceback.print_exc()

        return await handler(event, data)