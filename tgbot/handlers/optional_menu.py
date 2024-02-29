from datetime import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from models.db import DB
from tgbot.text import TEXT
from tgbot.keyboard import (get_choose_role_kb, get_choose_group_kb, get_choose_teacher_kb, get_choose_schedule,
                            get_letter_of_teacher_kb, options_kb, get_choose_weekday_kb, choose_lessons_kb)
from models.database import get_async_session
from tgbot.handlers.auxiliary import Form, bot
from tgbot.sesc_info import SESC_Info
from tgbot.handlers.registration import func_start_registration
from tgbot.parser import PARSER

router = Router()


class OptionalMenuMachine(Form):
    weekday_for_free_auditory = State()
    lesson_for_free_auditory = State()


@router.callback_query(F.data == 'optional_func')
async def optional_func(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.clear()
    await state.update_data(prev=func_start_registration)

    await bot.edit_message_text(text=TEXT('choose_optional_function', lang),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=options_kb(lang))
    await callback.answer()


@router.callback_query(F.data == 'free_auditory')
async def free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(prev=optional_func)
    await state.set_state(OptionalMenuMachine.weekday_for_free_auditory)

    await bot.edit_message_text(text=TEXT('choose_day', lang),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=get_choose_weekday_kb(lang))
    await callback.answer()


@router.callback_query(OptionalMenuMachine.weekday_for_free_auditory)
async def weekday_for_free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(weekday_for_free_auditory=callback.data)
    await state.set_state(OptionalMenuMachine.lesson_for_free_auditory)
    await state.update_data(prev=free_auditory)

    await bot.edit_message_text(text=TEXT('choose_lesson', lang),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=choose_lessons_kb(lang))

    await callback.answer()


@router.callback_query(OptionalMenuMachine.lesson_for_free_auditory)
async def send_free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(lesson_for_free_auditory=callback.data)
    data = await state.get_data()
    await state.clear()

    free = await PARSER.get_free_auditories(int(data.get('weekday_for_free_auditory')),
                                            int(data.get('lesson_for_free_auditory')))
    separator = ' | '  # разделитель между цифрами
    free_on_one_line = 6  # кол-во чисел на одной строчке
    free_str = ''  # итоговая строчка, которую будем отправлять

    for num, lesson in enumerate(free):
        if num % free_on_one_line == 0:
            free_str += '\n'
        free_str += lesson + separator

    free_str = free_str[:-len(separator)]  # обрезаем последний separator

    await bot.edit_message_text(text=free_str,
                                chat_id=chat_id,
                                message_id=message_id)

    # отправка основного сообщения
    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)
    await callback.answer()
