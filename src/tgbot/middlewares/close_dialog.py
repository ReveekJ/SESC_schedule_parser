from typing import Awaitable, Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.tgbot.text import BottomMenuText


class CloseDialogsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        try:
            if isinstance(event, Message):
                if event.text in [i.value for i in BottomMenuText]:
                    # завершаем все диалоги
                    dialog_manager = data.get('dialog_manager')
                    await dialog_manager.done()
        except Exception as e:  # возникает когда нет открытых диалогов
            pass

        await handler(event, data)
