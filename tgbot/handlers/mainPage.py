from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from tgbot.parser import PARSER
from models.db import DB
from models.database import get_async_session
import datetime

from tgbot.text import TEXT
from tgbot.keyboard import get_choose_schedule, get_choose_weekday_kb

router = Router()


@router.callback_query(F.data == 'today')
async def send_schedule_for_today(callback: CallbackQuery):
    session = await get_async_session()
    user_data = await DB().select_user_by_id(session, callback.from_user.id)
    lang = callback.from_user.language_code

    await callback.message.delete()

    file = PARSER.parse(user_data['role'], user_data['sub_info'],
                        str((datetime.date.today().weekday()) % 6 + 1))

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await callback.message.answer_photo(
            schedule,
            caption=TEXT('main', lang) + TEXT('weekdays', lang)[datetime.date.today().weekday() % 6 + 1],
            disable_notification=True)

    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)
    await callback.answer()


@router.callback_query(F.data == 'tomorrow')
async def send_schedule_for_tomorrow(callback: CallbackQuery):
    session = await get_async_session()
    user_data = await DB().select_user_by_id(session, callback.from_user.id)
    lang = callback.from_user.language_code

    await callback.message.delete()

    today = str((datetime.date.today().weekday() + 2) % 6)
    file = PARSER.parse(user_data['role'], user_data['sub_info'], today)

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)

        await callback.message.answer_photo(
            schedule,
            caption=TEXT('main', lang) + TEXT('weekdays', lang)[(datetime.date.today().weekday() + 2) % 6],
            disable_notification=True)

    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)
    await callback.answer()


@router.callback_query(F.data == 'all_days')
async def get_all_days_sch(callback: CallbackQuery):
    lang = callback.from_user.language_code

    await callback.message.delete()
    await callback.message.answer(TEXT('choose_day', lang),
                                  reply_markup=get_choose_weekday_kb(lang),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(F.data in [str(i) for i in range(1, 7)])
async def get_sch_for_this_day(callback: CallbackQuery):
    lang = callback.from_user.language_code
    session = await get_async_session()
    user_data = await DB().select_user_by_id(session, callback.from_user.id)
    file = PARSER.parse(user_data['role'], user_data['sub_info'], callback.data)

    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await callback.message.answer_photo(
            schedule,
            caption=TEXT('main', lang) + TEXT('weekdays', lang)[int(callback.data)],
            disable_notification=True)

    await callback.answer()
    