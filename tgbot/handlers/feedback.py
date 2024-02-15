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


@router.message(ChatTypeFilter(chat_ignor_type=['group', 'supergroup']) and F.video)
async def feedback_photo(message: Message):
    path_to_feedback = f"{__file__[:__file__.rfind('/', 0, __file__.rfind('/', 0, __file__.rfind('/')))] + '/temp/' + str(uuid.uuid4())}"
    if message.content_type == ContentType.PHOTO:
        await bot.download(
            message.photo[-1],
            destination=path_to_feedback + '.png')
        image_from_pc = FSInputFile(path_to_feedback)

        for admin in ADMINS:
            await bot.send_photo(admin, image_from_pc,
                                 disable_notification=True)

    elif message.content_type == ContentType.VIDEO:
        # await bot.download(
        #     message.video,
        #     destination=path_to_feedback + '.mp4')
        video = message.video.file_id

        for admin in ADMINS:
            await bot.send_video(admin, video,
                                 disable_notification=True)

    elif message.content_type == ContentType.VOICE:
        # await bot.download(
        #     message.audio[-1],
        #     destination=path_to_feedback + '.mp3')
        # image_from_pc = FSInputFile(path_to_feedback)
        image_from_pc = message.voice.file_id
        for admin in ADMINS:
            await bot.send_voice(admin, image_from_pc,
                                 disable_notification=True)
    elif message.content_type == ContentType.VIDEO_NOTE:
        await bot.download(
            message.video_note[-1],
            destination=path_to_feedback + '.mp4')
        image_from_pc = FSInputFile(path_to_feedback)
        for admin in ADMINS:
            await bot.send_video(admin, image_from_pc,
                                 disable_notification=True)
    elif message.content_type == ContentType.ANIMATION:
        await bot.download(
            message.animation[-1],
            destination=path_to_feedback + '.mp4')
        image_from_pc = FSInputFile(path_to_feedback)
        for admin in ADMINS:
            await bot.send_video(admin, image_from_pc,
                                 disable_notification=True)