from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile

from tgbot.handlers.auxiliary import Form, bot
from tgbot.handlers.auxiliary import send_schedule
from tgbot.handlers.registration import func_start_registration
from tgbot.keyboard import (get_choose_group_kb, get_choose_weekday_kb, get_choose_auditory_kb,
                            get_choose_teacher_kb, get_choose_schedule, get_letter_of_teacher_kb)
from tgbot.parser import PARSER
from tgbot.sesc_info import SESC_Info
from tgbot.text import TEXT


class AllScheduleMachine(Form):
    type = State()
    letter_of_teacher = State()
    second = State()
    weekday = State()


router = Router()

'''-------- ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ -------------'''


async def func_get_group(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data.split('_')[-1]
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    p = [get_choose_auditory_kb, get_letter_of_teacher_kb, get_choose_group_kb]
    keyboards = {e: p[i] for i, e in enumerate(SESC_Info.TYPE.values()) if e != 'all'}

    await state.update_data(prev=func_start_registration)

    await state.update_data(type=data)
    await state.set_state(AllScheduleMachine.second)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_sub_info_' + data if data != 'teacher' else 'choose_letter', lang),
                                reply_markup=keyboards[data](lang))

    await callback.answer()


async def func_second_teacher(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=func_start_registration)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_sub_info_teacher', lang),
                                reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang))

    await callback.answer()


async def func_second(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    await state.update_data(prev=func_start_registration)
    await state.update_data(second=data)
    await state.set_state(AllScheduleMachine.weekday)

    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=TEXT('choose_day', lang),
                                reply_markup=get_choose_weekday_kb(lang))

    await callback.answer()


async def func_weekday(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = await state.get_data()
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    _type = data['type']
    _second = data['second']
    _weekday = callback.data

    await state.clear()

    file = await PARSER.parse(_type, _second, _weekday)

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=message_id,
                                    text=TEXT('no_schedule', lang))
    else:
        schedule = FSInputFile(file)
        await callback.message.delete()
        await send_schedule(chat_id=user_id,
                            short_name_text_mes='main_schedule',
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


@router.callback_query(F.data == 'type_group')
@router.callback_query(F.data == 'type_teacher')
@router.callback_query(F.data == 'type_auditory')
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
