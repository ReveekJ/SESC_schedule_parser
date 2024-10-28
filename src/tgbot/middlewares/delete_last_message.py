from typing import Awaitable, Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject, Message

from src.tgbot.text import BottomMenuText
from src.tgbot.user_models.db import DB
from src.utils.aiogram_utils import delete_last_message


class DeleteLastMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        try:
            if isinstance(event, Message):
                texts = []
                for i in BottomMenuText:
                    for j in i.value.values():
                        texts.append(j)

                if event.text in texts:
                    # удаляем последнее, уже не нужное сообщение
                    await delete_last_message(event.from_user.id)
        except Exception as e:  # возникает когда сообщения не существует
            print(e)

        message = await handler(event, data)
        # pprint(message)

        # сохраняем последний id
        if isinstance(message, Message):
            if isinstance(event, (Message, CallbackQuery)):
                user_id = event.from_user.id
                await DB().update_last_message_id(user_id, message.message_id)


class SaveLastMessageIdMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        message = await handler(event, data)

        # сохраняем последний id
        if isinstance(message, Message):
            if isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                await DB().update_last_message_id(user_id, message.message_id)
