import datetime
from enum import Enum

from aiogram.types import User
from aiogram_dialog import DialogManager

from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.states import AdminMachine
from src.tgbot.sesc_info import SESC_Info
from src.tgbot.text import TEXT


class ElectiveInfo(Enum):
    elective_times = sorted([datetime.time(8, 10), datetime.time(11, 40), datetime.time(15, 30),
                             datetime.time(19, 0), datetime.time(19, 40), datetime.time(17, 0),
                             datetime.time(18, 15), datetime.time(14, 15), datetime.time(13, 15),
                             datetime.time(18, 30), datetime.time(20, 0), datetime.time(21, 0),
                             datetime.time(9, 0), datetime.time(17, 30)])
    date_format: str = '%H:%M'


def __list_to_select_format(items: list, custom_index: list | None = None) -> list[tuple]:
    return [(index, elem) for index, elem in zip(range(len(items)) if custom_index is None else custom_index, items)]


async def lang_getter(event_from_user: User, **kwargs) -> dict:
    return {'lang': event_from_user.language_code}


async def pulpit_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    pulpit = SESC_Info.PULPIT.get(lang)

    if dialog_manager.dialog_data.get('action') == 'add':
        return {'pulpit': __list_to_select_format(pulpit),
                'lang': lang}

    return {'pulpit': __list_to_select_format((await ElectiveCourseDB.get_exist_pulpits())),
            'lang': lang}


async def possible_days_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    name_of_course = dialog_manager.dialog_data.get('name_of_course')
    possible_days = [i.weekday for i in (await ElectiveCourseDB.get_courses_by_subject(name_of_course))]
    # print(possible_days)
    # print((await ElectiveCourseDB.get_courses_by_subject(name_of_course)))
    # print(name_of_course)
    # print(dialog_manager.dialog_data)
    possible_days = [TEXT('weekdays_kb', lang)[i] for i in (possible_days if possible_days != [] else
                                                            [i for i in range(1, 8)])]
    return {
        'lang': lang,
        'possible_days': __list_to_select_format(possible_days)
    }


async def courses_by_pulpit_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    pulpit = dialog_manager.dialog_data.get('pulpit')
    row_data = await ElectiveCourseDB.get_courses_by_pulpit(pulpit)
    courses = list(set(i.subject for i in row_data))
    return {'lang': lang,
            'courses': __list_to_select_format(courses)}


async def __time_getter(event_from_user: User, dialog_manager: DialogManager, prev_time: datetime.time | None,
                        **kwargs):
    lang = (await lang_getter(event_from_user)).get('lang')
    times = ElectiveInfo.elective_times.value.copy()
    time_from = dialog_manager.dialog_data.get('time_from')

    if dialog_manager.dialog_data.get('action') != 'add':
        # prev_time = ((await ElectiveCourseDB.get_courses_by_subject(dialog_manager.dialog_data.get('name_of_course')))
        #              [0].time_from)
        # await dialog_manager.update({'prev_time': prev_time})
        times.remove(prev_time)

    if dialog_manager.current_context().state == AdminMachine.time_to:
        try:
            time_from_index = times.index(time_from)
            times = times[time_from_index + 1:]
        except ValueError:  # возникает когда time_from - это old_time для time_to
            for index, elem in enumerate(times):
                if elem > time_from:
                    times = times[index:]
                    break
    else:  # state == AdminMachine.time_from
        times.pop(-1)

    return {
        'lang': lang,
        'time': __list_to_select_format([i.strftime(ElectiveInfo.date_format.value) for i in times]),
        'prev_time': prev_time.strftime(ElectiveInfo.date_format.value) if (prev_time is not None) else None,
        # Pycharm gone crazy, but it works
        'prev_time_exist': True if (dialog_manager.dialog_data.get('action') != 'add') and
                                   (prev_time > time_from if time_from is not None else True) else False,
    }


async def time_from_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    # записываем в dialog_data то, что отправилось как data_for_next_dialog
    start_data = dialog_manager.start_data
    if start_data is not None:
        dialog_manager.dialog_data.update(start_data)

    prev_time = dialog_manager.dialog_data.get('course').time_from if (dialog_manager.dialog_data.get('course')
                                                                       is not None) else None
    return await __time_getter(event_from_user, dialog_manager, prev_time)


async def time_to_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    prev_time = dialog_manager.dialog_data.get('course').time_to if (dialog_manager.dialog_data.get('course')
                                                                     is not None) else None
    return await __time_getter(event_from_user, dialog_manager, prev_time)


async def teacher_letter_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    action = dialog_manager.dialog_data.get('action')
    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'action_not_add': True if action != 'add' else False,
        'old_teacher': SESC_Info.TEACHER_REVERSE[
            dialog_manager.dialog_data.get('course').teacher_name] if action != 'add' else None,
        'teacher_letter': __list_to_select_format(SESC_Info.TEACHER_LETTERS)
    }


async def teacher_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    letter = dialog_manager.dialog_data.get('teacher_letter')
    action = dialog_manager.dialog_data.get('action')
    teachers = [(number, name) for name, number in SESC_Info.TEACHER.items() if name[0] == letter]

    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'teacher': teachers,
        'action_not_add': True if action != 'add' else False,
        'old_teacher': SESC_Info.TEACHER_REVERSE[
            dialog_manager.dialog_data.get('course').teacher_name] if action != 'add' else None,
    }


async def auditory_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    old_auditory = dialog_manager.dialog_data.get('course').auditory if (dialog_manager.dialog_data.get('course')
                                                                         is not None) else None
    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'auditory': __list_to_select_format(SESC_Info.AUDITORY.keys()),
        'old_auditory': old_auditory,
        'action_not_add': True if dialog_manager.dialog_data.get('action') != 'add' else False,
    }