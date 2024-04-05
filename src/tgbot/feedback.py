from typing import Union

from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, ContentType

from config import ADMINS
from src.tgbot.auxiliary import bot, Form
from src.tgbot.main_work.registration import func_start_registration
from src.tgbot.keyboard import back_kb
from src.tgbot.text import TEXT

router = Router()


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_ignor_type: Union[str, list]):
        self.chat_type = chat_ignor_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type != self.chat_type
        else:
            return message.chat.type not in self.chat_type


class FeedbackMachine(Form):
    get_feedback = State()


@router.message(Command('feedback'))
async def get_feedback(message: Message, state: FSMContext):
    user_id = message.chat.id
    lang = message.from_user.language_code

    await state.set_state(FeedbackMachine.get_feedback)
    await state.update_data({'prev': func_start_registration})

    await message.delete()
    await bot.send_message(user_id,
                           TEXT('get_feedback', lang),
                           reply_markup=back_kb(lang),
                           disable_notification=True)


@router.message(ChatTypeFilter(chat_ignor_type=['group', 'supergroup']) and FeedbackMachine.get_feedback)
async def feedback_photo(message: Message, state: FSMContext):
    user_id = message.chat.id
    lang = message.from_user.language_code

    await state.clear()

    if message.content_type == ContentType.TEXT:
        for admin in ADMINS:
            await bot.send_message(admin, message.text,
                                   disable_notification=True)
    elif message.content_type == ContentType.PHOTO:
        for admin in ADMINS:
            await bot.send_photo(admin, message.photo[-1].file_id,
                                 caption=message.caption,
                                 disable_notification=True)
    elif message.content_type == ContentType.VIDEO:
        for admin in ADMINS:
            await bot.send_video(admin, message.video.file_id,
                                 caption=message.caption,
                                 disable_notification=True)
    elif message.content_type == ContentType.VOICE:
        for admin in ADMINS:
            await bot.send_voice(admin, message.voice.file_id,
                                 caption=message.caption,
                                 disable_notification=True)
    elif message.content_type == ContentType.VIDEO_NOTE:
        for admin in ADMINS:
            await bot.send_video_note(admin, message.video_note.file_id,
                                      disable_notification=True)
    elif message.content_type == ContentType.ANIMATION:
        for admin in ADMINS:
            await bot.send_animation(admin, message.animation.file_id,
                                     caption=message.caption,
                                     disable_notification=True)
    elif message.content_type == ContentType.DOCUMENT:
        for admin in ADMINS:
            await bot.send_document(admin, message.document.file_id,
                                    caption=message.caption,
                                    disable_notification=True)
    elif message.content_type == ContentType.STICKER:
        await bot.send_sticker(user_id,
                               'CAACAgIAAxkBAAIERmXPixX1Hku9oE_2_GB-RDfTNsq6AAKDNgACRnyhS_XSczMY6WQ-NAQ',
                               disable_notification=True)
    else:
        for admin in ADMINS:
            await bot.send_message(admin, message.content_type,
                                   disable_notification=True)

    await bot.send_message(user_id,
                           TEXT('feedback_done', lang),
                           disable_notification=True)
    await func_start_registration(message, state)
