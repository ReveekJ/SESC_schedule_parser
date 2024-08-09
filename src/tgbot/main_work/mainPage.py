import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager, StartMode

from src.database import get_async_session
from src.tgbot.auxiliary import send_schedule, bot
from src.tgbot.elective_course import states
from src.tgbot.keyboard import get_choose_schedule, get_choose_weekday_kb
from src.tgbot.parser import PARSER
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB

router = Router()


@router.callback_query(F.data == 'tomorrow')
@router.callback_query(F.data == 'today')
async def send_schedule_for_today(callback: CallbackQuery):
    session = await get_async_session()
    user_data = await DB().select_user_by_id(session, callback.message.chat.id)
    lang = callback.from_user.language_code

    await callback.message.delete()

    if callback.data == 'tomorrow':
        today_to_tomorrow = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '1', 6: '1'}
        day = today_to_tomorrow[datetime.date.today().weekday()]
    else:
        day = str((datetime.date.today().weekday()) % 6 + 1)

    file = await PARSER.parse(user_data['role'], user_data['sub_info'], day)

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

    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)
    await callback.answer()


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
    session = await get_async_session()
    user_data = await DB().select_user_by_id(session, callback.message.chat.id)
    file = await PARSER.parse(user_data['role'], user_data['sub_info'], callback.data)

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

    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(F.data == 'to_elective')
async def to_elective(callback: CallbackQuery, dialog_manager: DialogManager):

    lang = callback.from_user.language_code
    db_session = await get_async_session()
    user = await DB().select_user_by_id(db_session, callback.from_user.id)

    # is_auth_user = False

    # url = 'http://localhost:8000/lycreg/check_auth_data/'
    # params = {'login': user.login, 'password': user.password}
    #
    # async with aiohttp.ClientSession(trust_env=True) as session:
    #     async with session.get(url, params=params) as response:
    #         res = await response.text()
    #         if json.loads(res).get('status') == 200:
    #             is_auth_user = True

    if user.role in ['teacher', 'admin']:  # TODO: добавить обратно проверку is_auth
        await dialog_manager.start(states.AdminMachine.action, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(states.ElectiveCourseMachine.start, mode=StartMode.RESET_STACK)

    await callback.answer()
    await db_session.close()
