import datetime
import json
from types import NoneType

import aiohttp
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from nats.js import JetStreamContext

from src.config import NATS_DELAYED_CONSUMER_SUBJECT
from src.tgbot.auxiliary import bot
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.elective_text import ElectiveText
from src.utils.delayed_remove_elective_changes.publisher import delay_changes_removing
from .getters import ElectiveInfo
from .schemas import ElectiveCourse
from .states import AdminMachine, AuthMachine
from ..user_models.db import DB
from ...database import get_async_session


# from src.tgbot.elective_course.user_work import to_elective

#  проверить является ли юзер зарегистрированным учителем либо админом
#  если да, то предоставить такой функционао
#  1) добавить новый курс
#  2) удалить курс
#  3) посмотреть свои курсы (если ты учитель)
#  4) получить список текущих курсов в виде google sheet

async def save_login(message: Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data.update({'login': message.text,
                                       'login_message_id': message.message_id})
    await dialog_manager.next()


async def save_password_and_process_data(message: Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

    lang = message.from_user.language_code
    chat_id = message.chat.id
    login = dialog_manager.dialog_data.get('login')
    password = message.text

    db_session = await get_async_session()
    user = await DB().select_user_by_id(db_session, chat_id)

    url = 'http://localhost:8000/lycreg/check_auth_data/'
    params = {'role': user.role, 'login': login, 'password': password}

    async with aiohttp.ClientSession() as lycreg_session:
        async with lycreg_session.post(url, json=params) as response:
            res = await response.text()

    await db_session.close()
    await bot.delete_messages(chat_id=chat_id,
                              message_ids=[dialog_manager.dialog_data.get('login_message_id'), message.message_id])

    if json.loads(res).get('status') == 200:
        await DB().update_user_info(db_session, user.id, login=login, password=password)
        await dialog_manager.start(AdminMachine.action, mode=StartMode.RESET_STACK)
    else:
        await message.answer(ElectiveText.login_password_incorrect.value[lang])
        await dialog_manager.switch_to(AuthMachine.login)

async def __save_to_dialog_data(data, dialog_manager: DialogManager):
    await dialog_manager.update({dialog_manager.current_context().state.state.split(':')[-1]: data})


async def save_to_dialog_data_and_next(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                       **kwargs):
    await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)
    await dialog_manager.next()


async def pulpit_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    action = dialog_manager.dialog_data.get('action')

    await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)
    await dialog_manager.switch_to(
        AdminMachine.name_of_course_input if action == 'add' else AdminMachine.name_of_course_selector)


async def name_input_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    if not (await ElectiveCourseDB.get_courses_by_subject(message.text)):
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.update({'name_of_course': message.text})
        await dialog_manager.switch_to(AdminMachine.day_of_week)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=ElectiveText.same_name_already_exist.value[message.from_user.language_code])


async def back_to_name_input(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    if dialog_manager.dialog_data.get('action') == 'add':
        await dialog_manager.switch_to(AdminMachine.name_of_course_input)
    else:
        await dialog_manager.switch_to(AdminMachine.name_of_course_selector)


async def name_select_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, *args, **kwargs):
    data = callback.data.split(':')[-1]
    await dialog_manager.update({'name_of_course': data})

    await dialog_manager.switch_to(AdminMachine.day_of_week)
    # await dialog_manager.switch_to(AdminMachine.)


async def days_of_week_saver(callback: CallbackQuery, widget: MessageInput, dialog_manager: DialogManager, *args,
                             **kwargs):
    days = dialog_manager.dialog_data.get('days_of_week')
    data = int(callback.data.split(':')[-1])

    if not days:
        days = [data]
    elif data in days:
        days: list
        days.remove(data)
    else:
        days.append(data)

    await dialog_manager.update({'days_of_week': days})


async def switch_to_time_from_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                      **kwargs):
    if not dialog_manager.dialog_data.get('days_of_week'):
        return None

    days_of_week = sorted(dialog_manager.dialog_data.get('days_of_week'))
    await dialog_manager.update({'days_of_week': days_of_week})

    if dialog_manager.dialog_data.get('action') == 'remove':
        list_of_courses_for_remember = []
        js = dialog_manager.middleware_data.get('js')

        for day in days_of_week:
            #  используем заглушки так как в commit_changes все равно используется только subject и weekday
            course_for_remember = ElectiveCourse(
                subject=dialog_manager.dialog_data.get('name_of_course'),
                pulpit='',
                teacher_name='',
                weekday=day,
                time_from=datetime.time(0, 0, 0),
                time_to=datetime.time(0, 0, 0),
                auditory='',
            )
            list_of_courses_for_remember.append(course_for_remember)
        await commit_changes(dialog_manager.dialog_data.get('action'), list_of_courses_for_remember, js)

        await callback.message.delete()
        await dialog_manager.reset_stack()
        await dialog_manager.start(AdminMachine.action, mode=StartMode.NEW_STACK)  # возвращаемся
        return None

    await dialog_manager.switch_to(AdminMachine.time_from)


async def old_teacher_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data.update({'teacher': dialog_manager.dialog_data.get('course').teacher_name})
    await dialog_manager.switch_to(AdminMachine.auditory)


async def old_time_from_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                **kwargs):
    await __save_to_dialog_data(dialog_manager.dialog_data.get('course').time_from, dialog_manager)
    await dialog_manager.next()


async def old_time_to_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await __save_to_dialog_data(dialog_manager.dialog_data.get('course').time_to, dialog_manager)
    await dialog_manager.next()


async def time_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    row_data = callback.data.split(':')
    data = datetime.datetime.strptime(row_data[-2] + ':' + row_data[-1], ElectiveInfo.date_format.value).time()
    await __save_to_dialog_data(data, dialog_manager)
    await dialog_manager.next()


async def back_time_to_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data.pop('time_from', None)
    dialog_manager.dialog_data.pop('time_to', None)


async def back_teacher_letter_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                      **kwargs):
    dialog_manager.dialog_data.pop('time_to', None)


async def back_time_from_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                 **kwargs):
    if dialog_manager.dialog_data.get('cur_day_inx') is None:
        await dialog_manager.back()
    else:
        await dialog_manager.done(result={'back_time_from': True})


async def cancel_elective_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                  **kwargs):
    days_of_week = dialog_manager.dialog_data.get('days_of_week')
    cur_day_inx = dialog_manager.dialog_data.get('cur_day_inx', 0)

    old_course: ElectiveCourse = dialog_manager.dialog_data.get('course')
    course_for_remember = ElectiveCourse(
        subject=dialog_manager.dialog_data.get('name_of_course'),
        pulpit=dialog_manager.dialog_data.get('pulpit'),
        teacher_name=old_course.teacher_name,
        weekday=days_of_week[cur_day_inx],
        time_from=old_course.time_from,
        time_to=old_course.time_to,
        auditory=old_course.auditory,
        is_diffs=True,
        is_cancelled=True
    )

    lst = update_course_for_remember(course_for_remember, dialog_manager)
    await start_new_dialog(callback, dialog_manager, lst)

    # await dialog_manager.switch_to(AdminMachine)


async def start_new_dialog(callback: CallbackQuery, dialog_manager: DialogManager, list_of_courses_for_remember):
    cur_day_inx = dialog_manager.dialog_data.get('cur_day_inx', 0)
    days_of_week = dialog_manager.dialog_data.get('days_of_week')
    action = dialog_manager.dialog_data.get('action')

    if cur_day_inx + 1 == len(days_of_week):  # все дни прошли
        js = dialog_manager.middleware_data.get('js')
        await commit_changes(action, list_of_courses_for_remember, js)

        await callback.message.delete()
        await dialog_manager.reset_stack()
        await dialog_manager.start(AdminMachine.action, mode=StartMode.NEW_STACK)  # возвращаемся на главную
        return None

    # подготовка следующего диалога
    data_for_next_dialog: dict = dialog_manager.dialog_data.copy()
    data_for_next_dialog.update({'cur_day_inx': cur_day_inx + 1})
    for i in ('time_from', 'time_to', 'is_canceled', 'teacher_letter', 'teacher', 'auditory'):
        data_for_next_dialog.pop(i, None)

    await dialog_manager.start(AdminMachine.time_from, data=data_for_next_dialog)


def update_course_for_remember(course_for_remember: ElectiveCourse, dialog_manager: DialogManager) -> list[ElectiveCourse]:
    days_of_week = dialog_manager.dialog_data.get('days_of_week')
    cur_day_inx = dialog_manager.dialog_data.get('cur_day_inx', 0)
    list_of_courses_for_remember: list[ElectiveCourse] | None = dialog_manager.dialog_data.get('courses_for_remember')

    if isinstance(list_of_courses_for_remember, NoneType):
        list_of_courses_for_remember = [course_for_remember]
    else:
        if list_of_courses_for_remember[-1].weekday == days_of_week[cur_day_inx]:  # когда нажали на back
            list_of_courses_for_remember.pop(-1)
        list_of_courses_for_remember.append(course_for_remember)

    dialog_manager.dialog_data.update({'courses_for_remember': list_of_courses_for_remember})
    return list_of_courses_for_remember


async def auditory_handler(callback: CallbackQuery,
                           widget: Button,
                           dialog_manager: DialogManager,
                           *args, **kwargs):
    if callback.data == 'old_auditory':
        course: ElectiveCourse = dialog_manager.dialog_data.get('course')
        await __save_to_dialog_data(course.auditory, dialog_manager)
    else:
        await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)

    days_of_week: list = dialog_manager.dialog_data.get('days_of_week')
    cur_day_inx: int = dialog_manager.dialog_data.get('cur_day_inx', 0)
    action = dialog_manager.dialog_data.get('action')
    old_course: ElectiveCourse = dialog_manager.dialog_data.get('course')

    # сохранить информацию до лучших времен
    match action:
        #  секция remove находится в switch_to_time_from_handler
        case 'edit_for_one_day':
            course_for_remember = ElectiveCourse(
                subject=dialog_manager.dialog_data.get('name_of_course'),
                pulpit=dialog_manager.dialog_data.get('pulpit'),
                teacher_name=old_course.teacher_name,
                weekday=days_of_week[cur_day_inx],
                time_from=old_course.time_from,
                time_to=old_course.time_to,
                auditory=old_course.auditory,
                is_diffs=True,
                diffs_teacher=dialog_manager.dialog_data.get('teacher'),
                diffs_auditory=dialog_manager.dialog_data.get('auditory'),
                diffs_time_from=dialog_manager.dialog_data.get('time_from'),
                diffs_time_to=dialog_manager.dialog_data.get('time_to'),
                is_cancelled=False # True будет в отдельном хендлере на кнопку cancel
            )
        case _:  # case 'add' | 'edit_permanently'
            course_for_remember = ElectiveCourse(
                subject=dialog_manager.dialog_data.get('name_of_course'),
                pulpit=dialog_manager.dialog_data.get('pulpit'),
                teacher_name=dialog_manager.dialog_data.get('teacher'),
                weekday=days_of_week[cur_day_inx],
                time_from=dialog_manager.dialog_data.get('time_from'),
                time_to=dialog_manager.dialog_data.get('time_to'),
                auditory=dialog_manager.dialog_data.get('auditory'),
            )

    list_of_courses_for_remember = update_course_for_remember(course_for_remember, dialog_manager)

    await start_new_dialog(callback, dialog_manager, list_of_courses_for_remember)



async def commit_changes(action: str, changes_list: list[ElectiveCourse], js: JetStreamContext):
    match action:
        case 'add':
            for course in changes_list:
                await ElectiveCourseDB.add_course(course)
        case 'remove':
            weekdays = [course.weekday for course in changes_list]
            await ElectiveCourseDB.delete_course(changes_list[0].subject, weekdays)
        case 'edit_permanently':
            for course in changes_list:
                await ElectiveCourseDB.update_course(course, course.weekday)
        case 'edit_for_one_day':
            for course in changes_list:
                await ElectiveCourseDB.update_course(course, course.weekday)

                course_id = (await ElectiveCourseDB.get_course_by_subject_and_weekday(course.subject, course.weekday)).id
                now = datetime.datetime.now()
                day = datetime.datetime(now.year, now.month, now.day, 23, 59)
                removing_time = day + datetime.timedelta(days=course.weekday - day.weekday() - 1)
                await delay_changes_removing(js=js,
                                             course_id=course_id,  # нельзя course.id так как в course лежит курс взятый не из бд, а собранные в auditory_handler
                                             subject=NATS_DELAYED_CONSUMER_SUBJECT,
                                             removing_time=removing_time)
