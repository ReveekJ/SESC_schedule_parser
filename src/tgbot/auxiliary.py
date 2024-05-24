from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile

from ..config import TOKEN
from src.tgbot.sesc_info import SESC_Info
from src.tgbot.text import TEXT


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
            caption = (TEXT('main_schedule', lang) + ' ' + TEXT('weekdays', lang)[weekday] + ' ' +
                       SESC_Info.AUDITORY_REVERSE[sub_info])
        case _:
            caption = TEXT(short_name_text_mes, lang) + ' ' + TEXT('weekdays', lang)[weekday]

    await bot.send_photo(chat_id=chat_id,
                         photo=schedule,
                         caption=caption,
                         disable_notification=disable_notifications,
                         request_timeout=5)
