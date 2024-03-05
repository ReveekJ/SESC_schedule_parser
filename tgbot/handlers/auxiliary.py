from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile

from config import TOKEN
from models.database import get_async_session
from models.db import DB
from tgbot.parser import PARSER
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

    # await callback.message.delete()

    await func(callback, state)


async def send_schedule(chat_id: int, short_name_text_mes: str, role: str, sub_info: str, weekday: int, lang: str,
                        schedule: FSInputFile, disable_notifications: bool = True):
    match role:
        case 'teacher':
            caption = TEXT(short_name_text_mes, lang) + ' ' + TEXT('weekdays', lang)[weekday] + ' ' + \
                      SESC_Info.TEACHER_REVERSE[sub_info]
        case 'group':
            caption = TEXT(short_name_text_mes, lang) + ' ' + TEXT('weekdays', lang)[weekday] + ' ' + \
                      SESC_Info.GROUP_REVERSE[sub_info]
        case 'auditory':
            caption = (TEXT('main', lang) + ' ' + TEXT('weekdays', lang)[weekday] + ' ' +
                       SESC_Info.AUDITORY_REVERSE[sub_info])
        case _:
            caption = TEXT(short_name_text_mes, lang) + ' ' + TEXT('weekdays', lang)[weekday]

    await bot.send_photo(chat_id=chat_id,
                         photo=schedule,
                         caption=caption,
                         disable_notification=disable_notifications,
                         request_timeout=5)


async def sending_schedule_changes():
    # получаем измения
    changes = await PARSER.check_for_changes()

    for elem in changes:
        role = elem.type
        sub_info = elem.second
        weekday = elem.weekday
        # schedule = elem.schedule

        # создаем расписание с изменениями
        path = await PARSER.parse(str(role), str(sub_info), str(weekday))
        schedule = FSInputFile(path)

        session = await get_async_session()
        users = await DB().select_users_by_role_and_sub_info(session,
                                                             role=role,
                                                             sub_info=sub_info)
        # рассылаем изменения по юзерам
        for user_data in users:
            await send_schedule(chat_id=user_data['id'],
                                short_name_text_mes='changed_schedule',
                                role=role,
                                sub_info=sub_info,
                                weekday=int(weekday),
                                lang=user_data['lang'],
                                schedule=schedule,
                                disable_notifications=False)
