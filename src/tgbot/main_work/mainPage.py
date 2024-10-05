import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import DialogManager, StartMode

from src.config import ADMINS
from src.database import get_async_session
from src.tgbot.auxiliary import send_schedule, bot
from src.tgbot.elective_course import states
from src.tgbot.elective_course.user_work import UserWorkMachine
from src.tgbot.keyboard import get_choose_schedule, get_choose_weekday_kb
from src.tgbot.parser import PARSER
from src.tgbot.text import TEXT, BottomMenuText
from src.tgbot.user_models.db import DB

router = Router()


@router.callback_query(F.data == 'tomorrow')
@router.callback_query(F.data == 'today')
async def send_schedule_for_today(callback: CallbackQuery):
    lang = callback.from_user.language_code
    async with await get_async_session() as session:
        user_data = await DB().select_user_by_id(session, callback.message.chat.id)

    await callback.message.delete()

    if callback.data == 'tomorrow':
        today_to_tomorrow = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '1', 6: '1'}
        day = today_to_tomorrow[datetime.date.today().weekday()]
    else:
        day = str((datetime.date.today().weekday()) % 6 + 1)

    file = await PARSER.parse(user_data['role'], user_data['sub_info'], day, user_id=user_data.id)

    # проверка на присутствие расписания
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await send_schedule(chat_id=callback.message.chat.id,
                            lang=lang,
                            role=user_data['role'],
                            sub_info=user_data['sub_info'],
                            schedule=schedule,
                            short_name_text_mes='main_schedule',
                            weekday=int(day))

    await callback.answer()
    return (await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True))


@router.callback_query(F.data == 'all_days')
async def get_all_days_sch(callback: CallbackQuery):
    lang = callback.from_user.language_code
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=TEXT('choose_day', lang),
                                reply_markup=get_choose_weekday_kb(lang, back=False))

    await callback.answer()


@router.callback_query(F.data == '1')
@router.callback_query(F.data == '2')
@router.callback_query(F.data == '3')
@router.callback_query(F.data == '4')
@router.callback_query(F.data == '5')
@router.callback_query(F.data == '6')
async def get_sch_for_this_day(callback: CallbackQuery):
    lang = callback.from_user.language_code

    async with await get_async_session() as session:
        user_data = await DB().select_user_by_id(session, callback.message.chat.id)

    file = await PARSER.parse(user_data['role'], user_data['sub_info'], callback.data, user_id=user_data.id)

    await callback.message.delete()
    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang),
                                      disable_notification=True)
    else:
        schedule = FSInputFile(file)
        await send_schedule(chat_id=callback.message.chat.id,
                            schedule=schedule,
                            short_name_text_mes='main_schedule',
                            role=user_data['role'],
                            sub_info=user_data['sub_info'],
                            weekday=int(callback.data),
                            lang=lang)

    await callback.answer()
    return (await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True))


@router.message(F.text == BottomMenuText.electives.value)
async def to_elective(message: Message, dialog_manager: DialogManager):
    await message.delete()
    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, message.from_user.id)

    if user.id in ADMINS and user.role == 'teacher':
        await dialog_manager.start(states.AdminMachine.action, mode=StartMode.RESET_STACK)
    elif user.role in ['teacher', 'admin']:
        if user.is_approved_user:
            await dialog_manager.start(states.AdminMachine.action, mode=StartMode.RESET_STACK)
        else:
            await dialog_manager.start(states.AuthMachine.selfie, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(UserWorkMachine.start, mode=StartMode.RESET_STACK)

    await DB().update_last_message_id(message.from_user.id, user.last_message_id + 2)
