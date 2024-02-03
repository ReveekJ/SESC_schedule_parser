from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models.db import DB
from models.database import get_async_session

from tgbot.handlers.registration import func_start_registration, RegistrationMachine

from tgbot.text import TEXT
from tgbot.keyboard import hard_choice, get_choose_schedule

router = Router()


class ReloginMashine(RegistrationMachine):
    pass


@router.message(Command("relogin"))
async def relogin_confirmation(message: Message, state: FSMContext):
    lang = message.from_user.language_code

    await message.delete()
    await message.answer(TEXT("aus", lang),
                         reply_markup=hard_choice(lang=lang))


@router.callback_query(F.data == "relogin")
async def clear_user_data(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    user_id = callback.message.chat.id
    lang = callback.from_user.language_code

    await DB().delete_user(session, user_id)
    await callback.message.delete()

    await callback.message.answer(TEXT('hello', lang),
                                  disable_notification=True)
    await func_start_registration(callback, state)
    await callback.answer()


@router.callback_query(F.data == "reloginf")
async def cancel_deletion(callback: CallbackQuery):
    lang = callback.from_user.language_code

    await callback.message.delete()
    # отправка основного сообщения
    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)

    await callback.answer()
