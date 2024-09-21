from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.database import get_async_session
from src.tgbot.auxiliary import bot
from src.tgbot.main_work.registration import func_start_registration, RegistrationMachine
from src.tgbot.keyboard import hard_choice, get_choose_schedule
from src.tgbot.text import TEXT, MainText
from src.tgbot.user_models.db import DB

router = Router()


class ReloginMashine(RegistrationMachine):
    pass


@router.message(F.text == MainText.relogin.value)
async def relogin_confirmation(message: Message, state: FSMContext):
    lang = message.from_user.language_code
    chat_id = message.chat.id

    await message.delete()
    await bot.send_message(chat_id,
                           TEXT("aus", lang),
                           reply_markup=hard_choice(lang=lang),
                           disable_notification=True)


@router.callback_query(F.data == "relogin")
async def clear_user_data(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    user_id = callback.message.chat.id

    await DB().delete_user(session, user_id)
    await callback.message.delete()

    await func_start_registration(callback, state)
    await callback.answer()


@router.callback_query(F.data == "reloginf")
async def cancel_deletion(callback: CallbackQuery):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    # отправка основного сообщения
    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('main', lang),
                                reply_markup=get_choose_schedule(lang),
                                disable_notification=True)

    await callback.answer()
