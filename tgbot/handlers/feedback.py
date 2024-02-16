from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ContentType
from typing import Union
from aiogram.filters import BaseFilter
from config import ADMINS
from tgbot.handlers.auxiliary import bot
import uuid

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


@router.message(ChatTypeFilter(chat_ignor_type=['group', 'supergroup']))
async def feedback_photo(message: Message):
    if message.content_type == ContentType.PHOTO:
        for admin in ADMINS:
            await bot.send_photo(admin, message.photo[-1].file_id,
                                 disable_notification=True)
    elif message.content_type == ContentType.VIDEO:
        for admin in ADMINS:
            await bot.send_video(admin, message.video.file_id,
                                 disable_notification=True)
    elif message.content_type == ContentType.VOICE:
        for admin in ADMINS:
            await bot.send_voice(admin, message.voice.file_id,
                                 disable_notification=True)
    elif message.content_type == ContentType.VIDEO_NOTE:
        for admin in ADMINS:
            await bot.send_video_note(admin, message.video_note.file_id,
                                      disable_notification=True)
    elif message.content_type == ContentType.ANIMATION:
        for admin in ADMINS:
            await bot.send_animation(admin, message.animation.file_id,
                                     disable_notification=True)
    elif message.content_type == ContentType.DOCUMENT:
        for admin in ADMINS:
            await bot.send_animation(admin, message.document.file_id,
                                     disable_notification=True)
