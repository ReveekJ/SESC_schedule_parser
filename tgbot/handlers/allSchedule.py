from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from tgbot.parser import PARSER
from tgbot.text import TEXT
from tgbot.keyboard import (get_choose_type_kb, get_choose_group_kb, get_choose_weekday_kb, get_choose_auditory_kb,
                            get_choose_teacher_kb, get_choose_schedule, get_letter_of_teacher_kb)
from tgbot.sesc_info import SESC_Info
from tgbot.handlers.auxiliary import Form, bot
from tgbot.handlers.registration import func_start_registration
from tgbot.handlers.auxiliary import send_schedule


class AllScheduleMachine(Form):
    type = State()
    letter_of_teacher = State()
    second = State()
    weekday = State()


router = Router()

'''-------- ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ -------------'''


async def func_get_type(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    # если нажата назад, то отправится mainPage
    await state.clear()
    await state.set_state(AllScheduleMachine.type)
    await state.update_data(prev=func_start_registration)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await bot.send_message(user_id,
                           TEXT('choose_type', lang),
                           reply_markup=get_choose_type_kb(lang),
                           disable_notification=True)

    await callback.answer()


async def func_get_group(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data.split('_')[-1]
    user_id = callback.from_user.id

    p = [get_choose_auditory_kb, get_letter_of_teacher_kb, get_choose_group_kb]
    keyboards = {e: p[i] for i, e in enumerate(SESC_Info.TYPE.values()) if e != 'all'}

    await state.update_data(prev=func_get_type)

    await state.update_data(type=data)
    await state.set_state(AllScheduleMachine.second)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await bot.send_message(user_id,
                           TEXT('choose_sub_info_' + data if data != 'teacher' else 'choose_letter', lang),
                           reply_markup=keyboards[data](lang),
                           disable_notification=True)

    await callback.answer()


async def func_second_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    await state.update_data(prev=func_get_type)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await bot.send_message(user_id, text=TEXT('choose_sub_info_teacher', lang),
                           reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang),
                           disable_notification=True)

    await callback.answer()


async def func_second(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data
    user_id = callback.from_user.id

    await state.update_data(prev=func_get_type)
    await state.update_data(second=data)
    await state.set_state(AllScheduleMachine.weekday)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await bot.send_message(user_id, TEXT('choose_day', lang),
                           reply_markup=get_choose_weekday_kb(lang),
                           disable_notification=True)

    await callback.answer()


async def func_weekday(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = await state.get_data()
    user_id = callback.from_user.id

    _type = data['type']
    _second = data['second']
    _weekday = callback.data

    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    file = await PARSER.parse(_type, _second, _weekday)

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await send_schedule(chat_id=user_id,
                            short_name_text_mes='main',
                            role=_type,
                            sub_info=_second,
                            weekday=int(_weekday),
                            lang=lang,
                            schedule=schedule)
    # Send main page
    await bot.send_message(user_id,
                           TEXT('main', lang=lang),
                           reply_markup=get_choose_schedule(lang),
                           disable_notification=True)

    await callback.answer()


'''-------- ХЭНДЛЕРЫ -------------'''


@router.callback_query(F.data == 'see_all')
async def get_type(callback: CallbackQuery, state: FSMContext):
    await func_get_type(callback, state)


@router.callback_query(AllScheduleMachine.type)
async def get_group(callback: CallbackQuery, state: FSMContext):
    await func_get_group(callback, state)


@router.callback_query(AllScheduleMachine.second, F.data.startswith('letter_'))
async def second_teacher(callback: CallbackQuery, state: FSMContext):
    await func_second_teacher(callback, state)


@router.callback_query(AllScheduleMachine.second)
async def second(callback: CallbackQuery, state: FSMContext):
    await func_second(callback, state)


@router.callback_query(AllScheduleMachine.weekday)
async def weekday(callback: CallbackQuery, state: FSMContext):
    await func_weekday(callback, state)


# TODO: Доделать
# @router.callback_query(Form.type, F.data == 'type_all')
# async def get_all(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     data = callback.data.split('_')[-1]
#
#     await state.update_data(type=data)
#     await state.update_data(second='')
#     await state.set_state(Form.weekday)
#
#     await callback.message.delete()
#     await callback.message.answer(TEXT('choose_day', lang),
#                                   reply_markup=get_choose_weekday_kb(lang),
#                                   disable_notification=True)
#
#     await callback.answer()
