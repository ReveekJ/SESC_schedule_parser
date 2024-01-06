import asyncio
import time

from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from config import TOKEN
from tgbot.parser import PARSER
from models.db import DB
from models.database import get_async_session
import datetime

from tgbot.sesc_info import SESC_Info
from tgbot.text import TEXT


class Form(StatesGroup):
    prev = State()


router = Router()
bot = Bot(token=TOKEN)


@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    func = await state.get_data()
    func = func.get('prev')

    await callback.message.delete()

    await func(callback, state)


async def send_schedule(chat_id: int, short_name_text_mes: str, role: str, sub_info: str, weekday: int, lang: str,
                        schedule: FSInputFile):
    match role:
        case 'teacher':
            caption = TEXT(short_name_text_mes, lang) + TEXT('weekdays', lang)[weekday] + ' ' + \
                      SESC_Info.TEACHER_REVERSE[sub_info]
        case 'group':
            caption = TEXT(short_name_text_mes, lang) + TEXT('weekdays', lang)[weekday] + ' ' + \
                      SESC_Info.GROUP_REVERSE[sub_info]
        case 'auditory':
            caption = TEXT('main', lang) + TEXT('weekdays', lang)[weekday] + ' ' + SESC_Info.AUDITORY_REVERSE[sub_info]
        case _:
            caption = TEXT(short_name_text_mes, lang) + TEXT('weekdays', lang)[weekday]

    await bot.send_photo(chat_id=chat_id,
                         photo=schedule,
                         caption=caption,
                         disable_notification=True)


def convert_to_datetime_object(times: list[datetime.time]):
    result = []

    for i in times:
        result.append(datetime.datetime(2000, 1, 1,
                                        i.hour,
                                        i.minute,
                                        i.second))

    return result


def sending_schedule_changes():
    def merge_schedule(lessons: list[dict], diffs: list[dict]) -> list[dict]:
        merged_schedule = lessons

        for difference in diffs:
            number = difference['number']
            subgroup = difference['subgroup']

            for index, lesson in enumerate(merged_schedule):
                if lesson['number'] == number and lesson['subgroup'] == subgroup:
                    merged_schedule[index] = difference

        return merged_schedule

    async def inner():
        times = convert_to_datetime_object([datetime.time(0, 0, 0),
                                            datetime.time(5, 0, 0),
                                            datetime.time(6, 0, 0),
                                            datetime.time(7, 0, 0),
                                            datetime.time(12, 0, 0),
                                            datetime.time(15, 0, 0),
                                            datetime.time(18, 0, 0),
                                            datetime.time(20, 0, 0)])
        n = len(times)
        i = 0

        while True:
            groups_changes = await PARSER.check_for_changes_student()
            teachers_changes = await PARSER.check_for_changes_teacher()

            try:
                for elem in groups_changes.append(*teachers_changes):
                    role = elem[0]
                    sub_info = elem[1]
                    weekday = elem[2]
                    schedule = elem[3]

                    merged_schedule = merge_schedule(schedule['lessons'], schedule['diffs'])
                    # schedule = await PARSER.parse(role, sub_info, weekday)
                    path = PARSER.get_path(sub_info)
                    schedule = FSInputFile(PARSER.create_table(merged_schedule, path))

                    session = await get_async_session()
                    users = await DB().select_users_by_role_and_sub_info(session,
                                                                         role=role,
                                                                         sub_info=sub_info)

                    for user_data in users:
                        await send_schedule(chat_id=user_data['id'],
                                            short_name_text_mes='changed_schedule',
                                            role=role,
                                            sub_info=sub_info,
                                            weekday=weekday,
                                            lang=user_data['lang'],
                                            schedule=schedule)
            # возникает если пытаемся добавить пустой список
            except TypeError:
                pass
            time_to_sleep = abs(times[i % n] - convert_to_datetime_object([datetime.datetime.now().time()])[0])
            time.sleep(time_to_sleep.seconds)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(inner())
    loop.close()
