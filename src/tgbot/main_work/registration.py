import datetime
import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager

from src.config import ADMINS
from src.database import get_async_session
from src.tgbot.auxiliary import Form, bot
from src.tgbot.for_administration.administration_page import administration_page
from src.tgbot.keyboard import (get_choose_role_kb, get_choose_group_kb, get_choose_teacher_kb, get_choose_schedule,
                                get_letter_of_teacher_kb, aprove)
from src.tgbot.text import TEXT, BottomMenuText
from src.tgbot.user_models.db import DB
from src.tgbot.user_models.schemas import User
from pydantic import ValidationError


class RegistrationMachine(Form):
    role = State()
    letter_of_teacher = State()
    sub_info = State()
    lang = State()
    start_message_id = State()
    get_prove = State()


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
    current_user = await DB().select_user_by_id(session, user_id)

    if current_user is not None:
        await state.clear()
        # if current_user['role'] == 'administrator':
        #     await administration_page(message)
        if isinstance(message, CallbackQuery):
            msg = await bot.edit_message_text(chat_id=user_id,
                                        message_id=message_id,
                                        text=TEXT('main', lang=lang),
                                        reply_markup=get_choose_schedule(lang))
        else:
            msg = await bot.send_message(chat_id=user_id,
                                   text=TEXT('main', lang=lang),
                                   reply_markup=get_choose_schedule(lang),
                                   disable_notification=True)
        return msg

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


# фунция запрос на отправку фото пропуска(не уверен насчет перевода approve)
async def func_approve_admin(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=start_registration)
    await state.set_state(RegistrationMachine.get_prove)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('send_your_pass', lang))

    await callback.answer()


# отсылаем фотку действующим администраторам
async def func_send_verification_for_admins(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = await state.get_data()
    lang = data['lang']
    for admin in ADMINS:
        await bot.send_photo(admin, message.photo[-1].file_id,
                             caption=message.caption,
                             disable_notification=True,
                             reply_markup=aprove(lang, str(user_id)))
    await bot.send_message(user_id, text=TEXT('confirmation', lang))
    await func_start_registration(message, state)
    await state.clear()


# уведомляем администратора об одобрении, меняем роль или заканчиваем регистрацию
async def func_pozdravlenie(message: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    lang = message.from_user.language_code
    user_id = int(message.data.split('_')[1])
    user_data = await DB().select_user_by_id(session, user_id)

    if user_data:
        sub_role = user_data['sub_info']
        await DB().update_user_info(session,
                                    _id=user_id,
                                    role='administrator',
                                    sub_info=sub_role,
                                    lang=lang)
    else:
        try:
            await DB().create_user(session,
                                   User(id=user_id,
                                        role='administrator',
                                        sub_info='any',
                                        lang=lang))
        except ValidationError as e:
            logging.warning(str(datetime.datetime.now()) + ' ' + str(e))
            await bot.send_message(user_id, TEXT('reg_error', lang))
            await func_start_registration(message, state)
    await bot.send_message(user_id, text=TEXT("new_administrator_text", lang), disable_notification=True)
    await administration_page(message)
    await message.answer()


async def func_reject(callback: CallbackQuery):
    lang = callback.from_user.language_code
    user_id = int(callback.data.split('_')[1])
    await bot.send_message(user_id, text=TEXT("administrator_dismissed", lang), disable_notification=True)
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
    try:
        await DB().create_user(session,
                               User(id=chat_id,
                                    role=role,
                                    sub_info=sub_role,
                                    lang=lang))
    except Exception as e:
        logging.warning(str(datetime.datetime.now()) + ' ' + str(e))
        await callback.message.delete()
        await bot.send_message(chat_id, TEXT('reg_error', lang))
    else:
        #  сообщение о том что регистрация завершена
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=start_message_id,
                                    text=TEXT('registration_done', lang=lang))
        # отправляем основное сообщения
        msg = await bot.edit_message_text(chat_id=user_id,
                                    message_id=current_message_id,
                                    text=TEXT('main', lang=lang),
                                    reply_markup=get_choose_schedule(lang))
        await DB().update_last_message_id(user_id, msg.message_id)

    await callback.answer()


'''-------- ХЭНДЛЕРЫ -------------'''


@router.message(CommandStart())
@router.message(F.text == BottomMenuText.to_main.value['ru'])
@router.message(F.text == BottomMenuText.to_main.value['en'])
async def start_registration(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await message.delete()  # для красоты
    return await func_start_registration(message, state)


@router.callback_query(RegistrationMachine.role, F.data.casefold() == 'group')
async def set_role_student(callback: CallbackQuery, state: FSMContext):
    await func_set_role_student(callback, state)


@router.callback_query(RegistrationMachine.role, F.data.casefold() == 'teacher')
async def set_role_teacher(callback: CallbackQuery, state: FSMContext):
    await func_set_role_teacher(callback, state)


@router.callback_query(RegistrationMachine.role, F.data.casefold() == 'administration')
async def start_verification(callback: CallbackQuery, state: FSMContext):
    await func_approve_admin(callback, state)


@router.callback_query(RegistrationMachine.letter_of_teacher)
async def set_letter_of_teacher(callback: CallbackQuery, state: FSMContext):
    await func_set_letter_of_teacher(callback, state)


@router.callback_query(RegistrationMachine.sub_info)
async def set_sub_info(callback: CallbackQuery, state: FSMContext):
    await func_set_sub_info(callback, state)


@router.message(RegistrationMachine.get_prove)
async def send_verification_for_admins(message: Message, state: FSMContext):
    await func_send_verification_for_admins(message, state)


@router.callback_query(F.data.split('_')[2] == 'yes')
async def pozdravlenie(message: CallbackQuery, state: FSMContext):
    await func_pozdravlenie(message, state)


@router.callback_query(F.data.split('_')[2] == 'no')
async def rejected(message: CallbackQuery):
    await func_reject(message)
