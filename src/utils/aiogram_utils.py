from itertools import chain

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, User, Message

from src.database import get_async_session
from src.tgbot.auxiliary import bot
from src.tgbot.keyboard import get_choose_schedule
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB


class StartsWithFilter(Filter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, callback_query: CallbackQuery):
        return callback_query.data.startswith(self.prefix)



async def delete_last_message(user_id: int):
    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, user_id)

        try:
            await bot.delete_message(chat_id=user_id,
                                     message_id=user.last_message_id)
        except Exception:
            pass


async def send_main_page(user_id: int) -> Message:
    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, user_id)
    lang = user.lang

    return (await bot.send_message(chat_id=user_id,
                           text=TEXT('main', lang),
                           reply_markup=get_choose_schedule(lang),
                           disable_notification=True))