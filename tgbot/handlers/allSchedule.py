from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile

from tgbot.parser import PARSER
from tgbot.text import TEXT
from tgbot.keyboard import (get_choose_type_kb, get_choose_group_kb, get_choose_weekday_kb, get_choose_auditory_kb,
                            get_choose_teacher_kb, get_choose_schedule)
from tgbot.sesc_info import SESC_Info


class Form(StatesGroup):
    type = State()
    second = State()
    weekday = State()


router = Router()


@router.callback_query(F.data == 'see_all')
async def get_type(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    await state.set_state(Form.type)

    await callback.message.delete()
    await callback.message.answer(TEXT('choose_type', lang),
                                  reply_markup=get_choose_type_kb(lang),
                                  disable_notification=True)

    await callback.answer()


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


@router.callback_query(Form.type)
async def get_group(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data.split('_')[-1]
    p = [get_choose_auditory_kb, get_choose_teacher_kb, get_choose_group_kb]
    keyboards = {e: p[i] for i, e in enumerate(SESC_Info.TYPE.values()) if e != 'all'}

    await state.update_data(type=data)
    await state.set_state(Form.second)

    await callback.message.delete()
    await callback.message.answer(TEXT('choose_sub_info_' + data, lang),
                                  reply_markup=keyboards[data](lang),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(Form.second)
async def second(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = callback.data

    await state.update_data(second=data)
    await state.set_state(Form.weekday)
    await callback.message.delete()

    await callback.message.answer(TEXT('choose_day', lang),
                                  reply_markup=get_choose_weekday_kb(lang),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(Form.weekday)
async def weekday(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    data = await state.get_data()

    _type = data['type']
    _second = data['second']
    _weekday = callback.data

    await state.clear()

    await callback.message.delete()

    file = PARSER.parse(_type, _second, _weekday)

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)

        await callback.message.answer_photo(
            schedule,
            caption=TEXT('main', lang) + TEXT('weekdays', lang)[int(_weekday)],
            disable_notification=True)

    # Send main page
    await callback.message.answer(TEXT('main', lang=lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)

    await callback.answer()
