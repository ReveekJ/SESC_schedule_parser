from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery

from models.db import DB
from tgbot.text import TEXT
from tgbot.keyboard import (get_choose_role_kb, get_choose_group_kb, get_choose_teacher_kb, get_choose_schedule,
                            get_letter_of_teacher_kb)
from models.database import get_async_session
from tgbot.handlers.auxiliary import Form, bot


class RegistrationMachine(Form):
    role = State()
    letter_of_teacher = State()
    sub_info = State()
    lang = State()


router = Router()

'''-------- ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ -------------'''


# эта функция требуется для реализации кнопки back, тк мы не можем вызвать функцию, которая находится под декоратором
# так же мы должны использовать класс Bot для отправки сообщений, тк не получется отправить сообщение черз Message,
# но можно получить дополнительную информацию через message
async def func_start_registration(message: Message, state: FSMContext):
    session = await get_async_session()
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if await DB().select_user_by_id(session, user_id) is not None:
        await bot.send_message(user_id,
                               TEXT('main', lang=lang), reply_markup=get_choose_schedule(lang),
                               disable_notification=True)
        return None

    await state.update_data(lang=lang)
    await state.set_state(RegistrationMachine.role)

    await bot.send_message(message.from_user.id, TEXT('choose_role', lang=lang),
                           reply_markup=get_choose_role_kb(lang),
                           disable_notification=True)


async def func_set_role_student(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    await state.update_data(prev=func_start_registration)

    await state.update_data(role=callback.data)
    await state.set_state(RegistrationMachine.sub_info)

    await callback.message.delete()
    await bot.send_message(user_id,
                           TEXT('choose_sub_info_group', lang=lang),
                           reply_markup=get_choose_group_kb(lang),
                           disable_notification=True)

    await callback.answer()


async def func_set_role_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    await state.update_data(prev=start_registration)
    await state.update_data(role=callback.data)
    await state.set_state(RegistrationMachine.letter_of_teacher)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await bot.send_message(user_id,
                           TEXT('choose_letter', lang=lang),
                           reply_markup=get_letter_of_teacher_kb(lang),
                           disable_notification=True)

    await callback.answer()


async def func_set_letter_of_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    await state.update_data(prev=set_role_teacher)
    await state.set_state(RegistrationMachine.sub_info)

    await callback.message.delete()
    await bot.send_message(user_id,
                           text=TEXT('choose_sub_info_teacher', lang),
                           reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang),
                           disable_notification=True)

    await callback.answer()


async def func_set_sub_info(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    user_id = callback.from_user.id

    data = await state.get_data()
    await state.clear()
    # print(data)
    role = data['role']
    sub_role = callback.data
    lang = data['lang']
    chat_id = callback.from_user.id

    await DB().create_user(session,
                           id=chat_id,
                           role=role,
                           sub_info=sub_role,
                           lang=lang)

    await callback.message.delete()
    await bot.send_message(user_id,
                           TEXT('main', lang=lang),
                           reply_markup=get_choose_schedule(lang),
                           disable_notification=True)

    await callback.answer()


'''-------- ХЭНДЛЕРЫ -------------'''


@router.message(CommandStart())
async def start_registration(message: Message, state: FSMContext):
    lang = message.from_user.language_code
    await message.answer(TEXT('hello', lang),
                         disable_notification=True)
    await func_start_registration(message, state)


@router.callback_query(RegistrationMachine.role, F.data.casefold() == 'group')
async def set_role_student(callback: CallbackQuery, state: FSMContext):
    await func_set_role_student(callback, state)


@router.callback_query(RegistrationMachine.role, F.data.casefold() == 'teacher')
async def set_role_teacher(callback: CallbackQuery, state: FSMContext):
    await func_set_role_teacher(callback, state)


@router.callback_query(RegistrationMachine.letter_of_teacher)
async def set_letter_of_teacher(callback: CallbackQuery, state: FSMContext):
    await func_set_letter_of_teacher(callback, state)


@router.callback_query(RegistrationMachine.sub_info)
async def set_sub_info(callback: CallbackQuery, state: FSMContext):
    await func_set_sub_info(callback, state)
