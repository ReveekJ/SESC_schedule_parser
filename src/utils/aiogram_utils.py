from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from src.database import get_async_session
from src.tgbot.auxiliary import bot
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
