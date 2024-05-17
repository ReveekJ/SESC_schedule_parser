import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile

from src.tgbot.auxiliary import Form, send_schedule
from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.keyboard import get_elective_course_main_page_user_kb, get_choose_weekday_elective_kb
from src.tgbot.keyboard import get_choose_schedule
from src.tgbot.parser import ELECTIVE_PARSER
from src.tgbot.text import TEXT


class AddCourseMachine(Form):
    all_days = State()


router = Router()


@router.callback_query(F.data == 'to_elective')
async def to_elective(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    lang = callback.from_user.language_code
    await callback.message.edit_text(ElectiveText.main_page.value[lang],
                                     reply_markup=get_elective_course_main_page_user_kb(lang))
    await callback.answer()


@router.callback_query(F.data == 'today_elective_course')
@router.callback_query(F.data == 'tomorrow_elective_course')
async def get_elective_course(callback: CallbackQuery, state: FSMContext, weekday: int = None):
    await state.clear()

    lang = callback.from_user.language_code
    user_id = callback.from_user.id

    if weekday is not None:
        day = weekday
    elif callback.data == 'tomorrow_elective_course':
        today_to_tomorrow = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '1', 6: '1'}
        day = today_to_tomorrow[datetime.date.today().weekday()]
    else:
        day = str((datetime.date.today().weekday()) % 6 + 1)

    file = await ELECTIVE_PARSER.parse(user_id, weekday=day)
    await callback.message.delete()

    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await send_schedule(chat_id=callback.message.chat.id,
                            schedule=schedule,
                            short_name_text_mes='main_schedule',
                            role='elective',
                            sub_info='',
                            weekday=int(day),
                            lang=lang)

    await callback.message.answer(ElectiveText.main_page.value[lang],
                                  reply_markup=get_elective_course_main_page_user_kb(lang),
                                  disable_notification=True)
    await callback.answer()


@router.callback_query(F.data == 'all_days_elective_course')
async def all_days_elective_course(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    await state.update_data(prev=to_elective)

    await state.set_state(AddCourseMachine.all_days)
    await callback.message.edit_text(text=TEXT('choose_day', lang),
                                     reply_markup=get_choose_weekday_elective_kb(lang))

    await callback.answer()


@router.callback_query(AddCourseMachine.all_days)
async def elective(callback: CallbackQuery, state: FSMContext):
    await get_elective_course(callback, state, weekday=callback.data[9:])
    await callback.answer()


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    lang = callback.from_user.language_code
    await callback.message.edit_text(TEXT('main', lang),
                                     reply_markup=get_choose_schedule(lang),
                                     disable_notification=True)
    await callback.answer()
