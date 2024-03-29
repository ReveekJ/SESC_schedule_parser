from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery

from models.database import get_async_session
from models.db import DB
from tgbot.handlers.auxiliary import Form, bot
from tgbot.keyboard import (get_choose_role_kb, get_choose_group_kb, get_choose_teacher_kb, get_choose_schedule,
                            get_letter_of_teacher_kb)
from tgbot.text import TEXT


class RegistrationMachine(Form):
    role = State()
    letter_of_teacher = State()
    sub_info = State()
    lang = State()
    start_message_id = State()


router = Router()

'''-------- ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ -------------'''


# эта функция требуется для реализации кнопки back, тк мы не можем вызвать функцию, которая находится под декоратором
# так же мы должны использовать класс Bot для отправки сообщений, тк не получется отправить сообщение черз Message,
# но можно получить дополнительную информацию через message
async def func_start_registration(message: Message | CallbackQuery, state: FSMContext):
    session = await get_async_session()
    lang = message.from_user.language_code
    user_id = message.chat.id if isinstance(message, Message) else message.message.chat.id
    message_id = message.message_id if isinstance(message, Message) else message.message.message_id

    if await DB().select_user_by_id(session, user_id) is not None:
        await state.clear()
        if isinstance(message, CallbackQuery):
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=message_id,
                                        text=TEXT('main', lang=lang),
                                        reply_markup=get_choose_schedule(lang))
        else:
            await bot.send_message(chat_id=user_id,
                                   text=TEXT('main', lang=lang),
                                   reply_markup=get_choose_schedule(lang),
                                   disable_notification=True)
        return None
    data = await state.get_data()

    if data.get('role') is None:
        hello_text = TEXT('welcome', lang=lang) + message.from_user.full_name + '!\n' + TEXT('hello', lang=lang)
        msg = await bot.send_message(user_id,
                                     text=hello_text,
                                     disable_notification=True)
        await state.update_data(start_message_id=msg.message_id)

    await state.update_data(lang=lang)
    await state.set_state(RegistrationMachine.role)

    if isinstance(message, CallbackQuery) and message.message.text != TEXT('aus', lang):
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=message_id,
                                    text=TEXT('choose_role', lang=lang),
                                    reply_markup=get_choose_role_kb(lang))
    else:
        await bot.send_message(user_id, TEXT('choose_role', lang=lang),
                               reply_markup=get_choose_role_kb(lang),
                               disable_notification=True)


async def func_set_role_student(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=func_start_registration)

    await state.update_data(role=callback.data)
    await state.set_state(RegistrationMachine.sub_info)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_sub_info_group', lang=lang),
                                reply_markup=get_choose_group_kb(lang))

    await callback.answer()


async def func_set_role_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=start_registration)
    await state.update_data(role=callback.data)
    await state.set_state(RegistrationMachine.letter_of_teacher)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_letter', lang=lang),
                                reply_markup=get_letter_of_teacher_kb(lang))

    await callback.answer()


async def func_set_letter_of_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=set_role_teacher)
    await state.set_state(RegistrationMachine.sub_info)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_sub_info_teacher', lang),
                                reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang))

    await callback.answer()


async def func_set_sub_info(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    user_id = callback.message.chat.id
    current_message_id = callback.message.message_id

    data = await state.get_data()

    await state.clear()
    role = data['role']
    sub_role = callback.data
    lang = data['lang']
    chat_id = callback.message.chat.id
    start_message_id = data['start_message_id']

    # сохраняем пользователя в базу данных
    await DB().create_user(session,
                           id=chat_id,
                           role=role,
                           sub_info=sub_role,
                           lang=lang)

    # отправляем приветственное и основное сообщения
    await bot.edit_message_text(chat_id=user_id,
                                message_id=start_message_id,
                                text=TEXT('registration_done', lang=lang))

    await bot.edit_message_text(chat_id=user_id,
                                message_id=current_message_id,
                                text=TEXT('main', lang=lang),
                                reply_markup=get_choose_schedule(lang))

    await callback.answer()


'''-------- ХЭНДЛЕРЫ -------------'''


@router.message(CommandStart())
async def start_registration(message: Message, state: FSMContext):
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
