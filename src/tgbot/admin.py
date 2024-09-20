import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from src.config import ADMINS
from src.database import get_async_session
from src.tgbot.auxiliary import bot
from src.tgbot.elective_course.elective_text import AuthText
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB
from src.utils.aiogram_utils import StartsWithFilter

router = Router()


class SendToAllSG(StatesGroup):
    message = State()


@router.message(Command('send_to_all'))
async def send_to_all(message: Message, state: FSMContext):
    user_id = message.chat.id

    if user_id not in ADMINS:
        return None

    await state.set_state(SendToAllSG.message)


@router.message(SendToAllSG.message)
async def send_admin_message(message: Message):
    lang = message.from_user.language_code
    errors = 0

    async with await get_async_session() as session:
        users = await DB().get_all_users(session)

    for user in users:
        try:
            await message.send_copy(user.id)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            errors += 1

    await message.answer(TEXT('admin_sending_message', lang) + str(errors))


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
