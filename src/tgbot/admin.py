from aiogram import Router, F
from aiogram.filters import Command, Filter
from aiogram.types import Message, CallbackQuery

from src.config import ADMINS
from src.database import get_async_session
from src.tgbot.auxiliary import bot
from src.tgbot.elective_course.elective_text import AuthText
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB
from src.utils.aiogram_utils import StartsWithFilter

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


@router.callback_query(StartsWithFilter('selfie_'))
async def approve_teacher(callback: CallbackQuery):
    admin_id = callback.from_user.id

    if admin_id not in ADMINS:
        return None

    user_id, action = int(callback.data.split('_')[-1]), callback.data.split('_')[-2]

    if action == 'approve':
        async with await get_async_session() as session:
            await DB().update_user_info(session, user_id, is_approved_user=True)
            user = await DB().select_user_by_id(session, user_id)

        await bot.send_message(user_id, text=AuthText.you_approved.value[user.lang])
    else:
        async with await get_async_session() as session:
            await DB().update_user_info(session, user_id, is_approved_user=False)
            user = await DB().select_user_by_id(session, user_id)

        await bot.send_message(user_id, text=AuthText.you_declined.value[user.lang])

    await callback.answer()
