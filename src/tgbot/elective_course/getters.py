import datetime

from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedMultiselect

from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.states import AdminMachine
from src.tgbot.sesc_info import SESC_Info
from src.tgbot.text import TEXT
from .elective_info import ElectiveInfo
from ...utils.dialogs_utils import lang_getter, __list_to_select_format


async def pulpit_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')

    if dialog_manager.dialog_data.get('action') == 'add':
        pulpit = SESC_Info.PULPIT.get(lang)

        return {'pulpit': __list_to_select_format(pulpit, SESC_Info.PULPIT.get('en')),
                'lang': lang}

    pulpits = await ElectiveCourseDB.get_exist_pulpits()
    return {'pulpit': sorted(__list_to_select_format(pulpits.get(lang), pulpits.get('en')), key=lambda x: x[1]),
            'lang': lang}


async def possible_days_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    name_of_course = dialog_manager.dialog_data.get('name_of_course')
    possible_days_nums = [i.weekday for i in (await ElectiveCourseDB.get_courses_by_subject(name_of_course))]

    possible_days = [TEXT('weekdays_kb', lang)[i] for i in (possible_days_nums if possible_days_nums != [] else
                                                            [i for i in range(1, 8)])]
    res = sorted(__list_to_select_format(possible_days, possible_days_nums if possible_days_nums != [] else [i for i in range(1, 8)]), key=lambda x: x[0])

    #  геттер вызывается каждый раз, когда изменяется multiselect, так что мы должны проверить:
    #  мы еще ни разу не отмечали курсы (not is_set_checked_courses)
    #  функция вызывается юзером, а не учителем (isinstance(is_set_checked_courses, bool))
    is_set_checked_courses = dialog_manager.dialog_data.get('is_set_checked_courses')

    if (not is_set_checked_courses) and isinstance(is_set_checked_courses, bool):
        users_courses = await ElectiveCourseDB.get_elective_courses_by_user_id_and_course_name(event_from_user.id, name_of_course)
        multiselect: ManagedMultiselect = dialog_manager.find('weekdays_selector_userwork')
        await multiselect.reset_checked()

        for i in users_courses:
            await multiselect.set_checked(item_id=i.weekday,
                                          checked=True)

        dialog_manager.dialog_data.update({'is_set_checked_courses': True})

    return {
        'lang': lang,
        'possible_days': res
    }


async def courses_by_pulpit_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    pulpit = dialog_manager.dialog_data.get('pulpit')
    row_data = await ElectiveCourseDB.get_courses_by_pulpit(pulpit)
    courses = list(set(i.subject for i in row_data))
    return {'lang': lang,
            'courses': sorted(__list_to_select_format(courses), key=lambda x: x[1])}


def __get_weekday(dialog_manager: DialogManager, lang: str) -> str:
    return TEXT('weekdays', lang)[int(dialog_manager.dialog_data.get('days_of_week')[dialog_manager.dialog_data.get('cur_day_inx', 0)])]


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
        'prev_time_exist': True if (dialog_manager.dialog_data.get('action') != 'add') and
                                   (prev_time > time_from if time_from is not None else True) else False,
        'add_cancel': True if dialog_manager.dialog_data.get('action') == 'edit_for_one_day' else False,
        'weekday': __get_weekday(dialog_manager, lang),
    }


async def time_from_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    #  получаем старый курс
    try:
        current_weekday = dialog_manager.dialog_data.get('days_of_week')[dialog_manager.dialog_data.get('cur_day_inx',
                                                                                                        0)]
        old_course = await ElectiveCourseDB.get_course_by_subject_and_weekday(dialog_manager.dialog_data.get('name_of_course'),
                                                                              current_weekday)
        dialog_manager.dialog_data.update({'course': old_course})
    except Exception as e:
        print(e)
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
    lang = (await lang_getter(event_from_user)).get('lang')
    action = dialog_manager.dialog_data.get('action')
    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'action_not_add': True if action != 'add' else False,
        'old_teacher': SESC_Info.TEACHER_REVERSE[
            dialog_manager.dialog_data.get('course').teacher_name] if action != 'add' else None,
        'teacher_letter': __list_to_select_format(SESC_Info.TEACHER_LETTERS),
        'weekday': __get_weekday(dialog_manager, lang),
    }


async def teacher_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    letter = dialog_manager.dialog_data.get('teacher_letter')
    action = dialog_manager.dialog_data.get('action')
    teachers = [(number, name) for name, number in SESC_Info.TEACHER.items() if name[0] == letter]

    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'teacher': teachers,
        'action_not_add': True if action != 'add' else False,
        'old_teacher': SESC_Info.TEACHER_REVERSE[
            dialog_manager.dialog_data.get('course').teacher_name] if action != 'add' else None,
        'weekday': __get_weekday(dialog_manager, lang),
    }


async def auditory_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    old_auditory = SESC_Info.AUDITORY_REVERSE[dialog_manager.dialog_data.get('course').auditory] \
        if (dialog_manager.dialog_data.get('course') is not None) else None
    return {
        'lang': (await lang_getter(event_from_user)).get('lang'),
        'auditory': __list_to_select_format(SESC_Info.AUDITORY.keys(), custom_index=SESC_Info.AUDITORY.values()),
        'old_auditory': old_auditory,
        'action_not_add': True if dialog_manager.dialog_data.get('action') != 'add' else False,
        'weekday': __get_weekday(dialog_manager, lang),
    }


async def user_weekday_getter(event_from_user: User, **kwargs):
    lang = (await lang_getter(event_from_user)).get('lang')
    weekdays = TEXT('weekdays_kb', lang)
    return {'lang': lang,
            'weekdays': __list_to_select_format(list(weekdays.values()), [str(i) for i in weekdays.keys()])}
