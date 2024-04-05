from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMINS
from src.database import get_async_session
from src.tgbot.auxiliary import bot
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB

router = Router()


@router.message(Command('send_to_all'))
async def send_to_all(message: Message):
    user_id = message.chat.id

    if user_id not in ADMINS:
        return None

    session = await get_async_session()
    users = await DB().get_all_users(session)
    await session.close()

    text = message.text[13:]
    lang = message.from_user.language_code
    errors = 0

    for user in users:
        try:
            await bot.send_message(user['id'],
                                   text)
        except Exception as e:
            errors += 1

    await bot.send_message(user_id,
                           TEXT('admin_sending_message', lang) + str(errors))
