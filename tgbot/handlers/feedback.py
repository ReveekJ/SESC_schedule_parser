from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from typing import Union
import os
from aiogram.filters import BaseFilter
from config import ADMINS
from tgbot.handlers.auxiliary import bot

router = Router()

class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_ignor_type: Union[str, list]):
        self.chat_type = chat_ignor_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type != self.chat_type
        else:
            return message.chat.type not in self.chat_type

@router.message(ChatTypeFilter(chat_ignor_type=['group', 'supergroup']) and F.text)
async def feedback(message: Message):
    for admin in ADMINS:
        await bot.send_message(admin, message.text,
                               disable_notification=True)
@router.message(ChatTypeFilter(chat_ignor_type=['group', 'supergroup']) and F.photo)
async def feedback_photo(message: Message):
    path_to_feedback_photo = f"{__file__[:__file__.rfind('/', 0, __file__.rfind('/', 0, __file__.rfind('/')))] + '/temp/' + message.photo[-1].file_id}"
    await bot.download(
        message.photo[-1],
        destination=path_to_feedback_photo
    )
    image_from_pc = FSInputFile(path_to_feedback_photo)
    for admin in ADMINS:
        await bot.send_photo(admin, image_from_pc,
                               disable_notification=True)