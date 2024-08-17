import datetime
import json

import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile

from src.tgbot.auxiliary import Form, send_schedule
from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.keyboard import get_elective_course_main_page_user_kb, get_choose_weekday_elective_kb, \
    get_pulpit_kb, get_elective_kb, get_elective_course_main_page_admin_kb
from src.tgbot.keyboard import get_choose_schedule
from src.tgbot.parser import ELECTIVE_PARSER
from src.tgbot.text import TEXT
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.database import get_async_session
from src.tgbot.elective_course.elective_transactions.elective_transactions import ElectiveTransactions
from src.tgbot.user_models.db import DB


class ElectiveCourseMachine(Form):
    all_days = State()
    register_or_unsubscribe = State()
    choose_pulpit = State()
    choose_page = State()
    choose_elective = State()


router = Router()


@router.callback_query(F.data == 'to_elective')
async def to_elective(callback: CallbackQuery, state: FSMContext, edit_messages: bool = True):
    await state.clear()

    lang = callback.from_user.language_code
    db_session = await get_async_session()
    user = await DB().select_user_by_id(db_session, callback.from_user.id)

    # is_auth_user = False
    #
    # url = 'http://localhost:8000/lycreg/check_auth_data/'
    # params = {'login': user.login, 'password': user.password}
    #
    # async with aiohttp.ClientSession(trust_env=True) as session:
    #     async with session.get(url, params=params) as response:
    #         res = await response.text()
    #         if json.loads(res).get('status') == 200:
    #             is_auth_user = True

    if user.role in ['teacher', 'admin']:  # TODO: добавить обратно проверку is_auth
        if edit_messages:
            await callback.message.edit_text(ElectiveText.main_page.value[lang],
                                             reply_markup=get_elective_course_main_page_admin_kb(lang))
        else:
            await callback.message.answer(ElectiveText.main_page.value[lang],
                                          reply_markup=get_elective_course_main_page_admin_kb(lang))
    else:
        if edit_messages:
            await callback.message.edit_text(ElectiveText.main_page.value[lang],
                                             reply_markup=get_elective_course_main_page_user_kb(lang))
        else:
            await callback.message.answer(ElectiveText.main_page.value[lang],
                                          reply_markup=get_elective_course_main_page_user_kb(lang))

    await callback.answer()
    # await session.close()


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

    await state.set_state(ElectiveCourseMachine.all_days)
    await callback.message.edit_text(text=TEXT('choose_day', lang),
                                     reply_markup=get_choose_weekday_elective_kb(lang))

    await callback.answer()


@router.callback_query(ElectiveCourseMachine.all_days)
async def elective(callback: CallbackQuery, state: FSMContext):
    await get_elective_course(callback, state, weekday=callback.data[9:])
    await callback.answer()


@router.callback_query(F.data == 'register_to_new_course')
@router.callback_query(F.data == 'unsubscribe')
async def register_or_unsubscribe_to_new_course(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    if callback.data == 'register_to_new_course':
        await state.update_data(register_or_unsubscribe='register')
    else:
        await state.update_data(register_or_unsubscribe='unsubscribe')

    await state.update_data(prev=to_elective)
    await state.set_state(ElectiveCourseMachine.choose_pulpit)

    await callback.message.edit_text(text=ElectiveText.choose_pulpit.value[lang],
                                     reply_markup=get_pulpit_kb(lang))

    await callback.answer()


@router.callback_query(ElectiveCourseMachine.choose_pulpit)
async def choose_pulpit(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    session = await get_async_session()

    await state.update_data(prev=register_or_unsubscribe_to_new_course)
    await state.set_state(ElectiveCourseMachine.choose_elective)
    courses_from_the_pulpit = await ElectiveCourseDB.get_courses_by_pulpit(pulpit=callback.data)
    user_courses = await DB().select_user_by_id(session, callback.from_user.id)

    if len(courses_from_the_pulpit) >= 63:  # всего можно прикрепить 63 кнопки + 1 кнопка назад, но если
        # факультативов больше, то они все не влезут
        return None  # TODO: добавить обработку этого случая

    await callback.message.edit_text(text=ElectiveText.choose_elective.value[lang],
                                     reply_markup=get_elective_kb(lang, courses_from_the_pulpit,
                                                                  user_courses.elective_course_replied))

    await session.close()
    await callback.answer()


@router.callback_query(ElectiveCourseMachine.choose_elective)
async def choose_elective(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    session = await get_async_session()
    courses = await ElectiveCourseDB.get_courses_by_subject(callback.data)
    user = await DB().select_user_by_id(session, callback.from_user.id)
    data = await state.get_data()

    if data.get('register_or_unsubscribe') == 'register':
        for course in courses:
            await ElectiveTransactions.add_elective_transaction(session, user, course)
        await callback.message.edit_text(text=ElectiveText.successfully_register.value[lang])

    else:
        await ElectiveTransactions.delete_elective_transaction(session, user.id, courses)
        await callback.message.edit_text(text=ElectiveText.successfully_unsubscribe.value[lang])

    await callback.message.answer(ElectiveText.main_page.value[lang],
                                  reply_markup=get_elective_course_main_page_user_kb(lang),
                                  disable_notification=True)

    await state.clear()

    await callback.answer()


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    lang = callback.from_user.language_code
    await callback.message.edit_text(TEXT('main', lang),
                                     reply_markup=get_choose_schedule(lang),
                                     disable_notification=True)
    await callback.answer()
