from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from tgbot.parser import PARSER
from tgbot.sesc_info import SESC_Info
from models.db import DB

import datetime



router = Router()



@router.callback_query(F.data == 'today')
async def send_schedule_for_today(callback: CallbackQuery):
    session = DB()
    await session.connect()
    user_data = await session.select_user_by_id(callback.message.from_user.id)

    today = {i: j for j, i in SESC_Info.WEEKDAY}[(datetime.date.today().weekday()+ 1) % 6]
    PARSER.parse(user_data['role'], user_data['sub_info'], today)
    schedule = FSInputFile(f"schedules/{user_data['role']}_{user_data['sub_info']}_{today}.png")
    result = await callback.message.answer_photo(
        schedule,
        caption=""
    )
    await callback.message.answer(result.photo[-1].file_id)
@router.callback_query(F.data == 'tomorrow')
async def send_schedule_for_tomorrow(callback: CallbackQuery):
    session = DB()
    await session.connect()
    user_data = await session.select_user_by_id(callback.message.from_user.id)

    today = {i: j for j, i in SESC_Info.WEEKDAY}[(datetime.date.today().weekday()+ 2) % 6]
    PARSER.parse(user_data['role'], user_data['sub_info'], today)
    schedule = FSInputFile(f"schedules/{user_data['role']}_{user_data['sub_info']}_{today}.png")
    result = await callback.message.answer_photo(
        schedule,
        caption=""
    )
    await callback.message.answer(result.photo[-1].file_id)

#@router.callback_query(F.data == 'all')
#async def send_all_schedule(callback: CallbackQuery):
