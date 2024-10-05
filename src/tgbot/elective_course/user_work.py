import datetime

from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button, Multiselect, ManagedMultiselect

from src.database import get_async_session
from src.tgbot.auxiliary import send_schedule
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.elective_transactions.elective_transactions import ElectiveTransactions
from src.tgbot.elective_course.schemas import UserWorkSchema, ElectiveCourse
from src.tgbot.elective_course.states import UserWorkMachine
from src.tgbot.parser import ELECTIVE_PARSER
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB
from src.utils.dialogs_utils import lang_getter, get_days_of_week


def get_user_work_schema(dialog_manager: DialogManager) -> UserWorkSchema:
    return dialog_manager.dialog_data.get('data') if dialog_manager.dialog_data.get('data') else UserWorkSchema()


def save_user_work_schema(dialog_manager: DialogManager, new_schema: UserWorkSchema) -> None:
    dialog_manager.dialog_data['data'] = new_schema

    # сохраняем данные из new_schema в обычный dialog_data для совместимости с геттерами админки
    for key, value in new_schema.model_dump().items():
        dialog_manager.dialog_data[key] = value


async def handle_schedule(callback: CallbackQuery, lang: str, day: str):
    user_id = callback.from_user.id
    file = await ELECTIVE_PARSER.parse(user_id, weekday=day)
    await callback.message.delete()

    if file == 'NO_SCHEDULE':
        await callback.message.answer(TEXT('no_schedule', lang), disable_notification=True)
    else:
        schedule = FSInputFile(file)

        await send_schedule(chat_id=callback.message.chat.id,
                            schedule=schedule,
                            short_name_text_mes='main_schedule',
                            role='elective',
                            sub_info='',
                            weekday=int(day),
                            lang=lang)


async def on_today(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    lang = callback.from_user.language_code
    day = str((datetime.date.today().weekday()) % 6 + 1)  # Today
    await handle_schedule(callback, lang, day)

    await dialog_manager.done()
    await dialog_manager.start(UserWorkMachine.start)

async def on_tomorrow(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    lang = callback.from_user.language_code
    today_to_tomorrow = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '1', 6: '1'}
    day = today_to_tomorrow[datetime.date.today().weekday()]  # Tomorrow
    await handle_schedule(callback, lang, day)

    await dialog_manager.done()
    await dialog_manager.start(UserWorkMachine.start)

async def on_any_weekday(callback: CallbackQuery,
                         widget: Button,
                         dialog_manager: DialogManager,
                         *args, **kwargs):
    lang = callback.from_user.language_code

    await handle_schedule(callback, lang, str(callback.data.split(':')[-1]))

    await dialog_manager.done()
    await dialog_manager.start(UserWorkMachine.start)

async def user_pulpit_handler(callback: CallbackQuery,
                              widget: Button,
                              dialog_manager: DialogManager,
                              *args, **kwargs):
    data = get_user_work_schema(dialog_manager)
    data.pulpit = callback.data.split(':')[-1]

    save_user_work_schema(dialog_manager, data)
    await dialog_manager.switch_to(UserWorkMachine.choose_elective)


async def user_course_handler(callback: CallbackQuery,
                              widget: Button,
                              dialog_manager: DialogManager,
                              *args, **kwargs):
    data = get_user_work_schema(dialog_manager)
    data.name_of_course = callback.data.split(':')[-1]

    save_user_work_schema(dialog_manager, data)
    dialog_manager.dialog_data.update({'is_set_checked_courses': False})
    await dialog_manager.switch_to(UserWorkMachine.choose_weekday)


async def register_to_electives(callback: CallbackQuery,
                                widget: Button,
                                dialog_manager: DialogManager,
                                *args, **kwargs):
    data = get_user_work_schema(dialog_manager)
    user_id = callback.from_user.id
    user_lang = (await lang_getter(callback.from_user)).get('lang')

    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, user_id)

        #  получаем id курсов с названием, которое выбрал юзер, на которые он подписан
        old_courses: list[ElectiveCourse] = []
        for course in user.elective_course_replied:
            if course.subject == data.name_of_course:
                old_courses.append(course)

        #  удаляем все полученные курсы
        #  (это немного нагружает систему, но нагрузки много не будет так что норм)
        await ElectiveTransactions.delete_elective_transaction(session, user_id, old_courses)

        weekdays = get_days_of_week('weekdays_selector_userwork', dialog_manager)

        #  регистрируем на новые курсы
        for weekday in weekdays:
            course = await ElectiveCourseDB.get_course_by_subject_and_weekday(data.name_of_course, int(weekday))
            await ElectiveTransactions.add_elective_transaction(session, user, course)

    await callback.message.answer(ElectiveText.successfully_sub_or_unsub.value[user_lang])
    await dialog_manager.done()
    await dialog_manager.start(UserWorkMachine.start,
                               mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.DELETE_AND_SEND)
