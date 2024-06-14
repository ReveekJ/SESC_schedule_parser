import datetime
from enum import Enum

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.keyboard import add_back_btn
from src.tgbot.text import TEXT
from src.tgbot.sesc_info import SESC_Info


class ElectiveInfo(Enum):
    elective_times = sorted([datetime.time(8, 10), datetime.time(11, 40), datetime.time(15, 30),
                             datetime.time(19, 0), datetime.time(19, 40), datetime.time(17, 0),
                             datetime.time(18, 15), datetime.time(14, 15), datetime.time(13, 15),
                             datetime.time(18, 30), datetime.time(20, 0), datetime.time(21, 0),
                             datetime.time(9, 0), datetime.time(17, 30)])
    date_format = '%H:%M'


def get_elective_course_main_page_admin_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ElectiveText.add.value[lang], callback_data='add')
    kb.button(text=ElectiveText.remove.value[lang], callback_data='remove')
    kb.button(text=ElectiveText.edit_from_one_day.value[lang], callback_data='edit_for_one_day')
    kb.button(text=ElectiveText.edit_permanently.value[lang], callback_data='edit_permanently')
    kb.button(text=ElectiveText.to_main.value[lang], callback_data='to_main')

    kb.adjust(1)
    return kb.as_markup()


def get_elective_course_main_page_user_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('today', lang), callback_data='today_elective_course')
    kb.button(text=TEXT('tomorrow', lang), callback_data='tomorrow_elective_course')
    kb.button(text=TEXT('all_days', lang), callback_data='all_days_elective_course')
    kb.button(text=ElectiveText.register_to_new_course.value[lang], callback_data='register_to_new_course')
    kb.button(text=ElectiveText.unsubscribe.value[lang], callback_data='unsubscribe')
    kb.button(text=ElectiveText.to_main.value[lang], callback_data='to_main')

    kb.adjust(1)
    return kb.as_markup()


def get_choose_weekday_elective_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    today = datetime.date.today().weekday() + 1
    kb.button(text=TEXT('today_btn', lang), callback_data='elective_' + str(today if today != 7 else 1))

    for callback_data, text in TEXT('weekdays_kb', lang).items():
        if callback_data == 7:
            continue

        kb.button(text=text, callback_data='elective_' + str(callback_data))

    add_back_btn(kb, lang)

    kb.adjust(1)
    return kb.as_markup()


def get_pulpit_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for index, elem in enumerate(SESC_Info.PULPIT[lang]):
        kb.button(text=elem, callback_data=SESC_Info.PULPIT['en'][index])

    add_back_btn(kb, lang)

    kb.adjust(1)
    return kb.as_markup()


# TODO: в клавиатуре должны быть только уникальные факультативы
def get_elective_kb(lang: str, courses: list[ElectiveCourse], users_elective_courses: list[ElectiveCourse]) -> (
        InlineKeyboardMarkup):
    kb = InlineKeyboardBuilder()

    for i in courses:
        kb.button(text='✅ ' + i.subject if i in users_elective_courses else i.subject, callback_data=i.subject)

    kb.adjust(2)
    add_back_btn(kb, lang)
    return kb.as_markup()


def get_back_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_back_btn(kb, lang)

    return kb.as_markup()


def get_are_you_sure_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text=ElectiveText.yes.value[lang], callback_data='yes')
    kb.button(text=ElectiveText.no.value[lang], callback_data='no')

    return kb.as_markup()


def get_choose_weekday_kb_elective(lang: str,
                                   selected_days: list[str | int],
                                   possible_days: dict[int, str] | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text=ElectiveText.done.value[lang], callback_data='done')

    for index, day in enumerate(selected_days):
        selected_days[index] = str(day)

    for callback_data, text in (TEXT('weekdays_kb', lang) if possible_days is None else possible_days).items():
        if callback_data == 7:
            continue
        if str(callback_data) in selected_days:
            kb.button(text='✅ ' + text, callback_data='elective_' + str(callback_data))
        else:
            kb.button(text=text, callback_data='elective_' + str(callback_data))

    add_back_btn(kb, lang)
    kb.adjust(1)

    return kb.as_markup()


def get_time_from_kb(lang: str, old_time: datetime.time | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    times = [i.strftime(str(ElectiveInfo.date_format.value)) for i in ElectiveInfo.elective_times.value]

    if old_time is not None:
        # если старого времени нет, то факультатива еще не существует, отменять нечего
        kb.button(text=ElectiveText.cancel_elective.value[lang], callback_data='cancel_elective')
        old_time = old_time.strftime(str(ElectiveInfo.date_format.value))
        kb.button(text=old_time, callback_data=old_time)

    for time in times:
        kb.button(text=time, callback_data=time)

    add_back_btn(kb, lang)
    kb.adjust(1)

    return kb.as_markup()


def get_time_to_kb(lang: str, time_from: datetime.time, old_time=None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if old_time is not None:
        old_time = old_time.strftime(str(ElectiveInfo.date_format.value))
        kb.button(text=old_time, callback_data=old_time)

    time_from_index = ElectiveInfo.elective_times.value.index(time_from)
    for time in ElectiveInfo.elective_times.value[time_from_index + 1:]:
        time = time.strftime(str(ElectiveInfo.date_format.value))
        kb.button(text=time, callback_data=time)

    add_back_btn(kb, lang)
    kb.adjust(1)
    return kb.as_markup()


def get_teacher_letter_kb(lang: str, old_teacher: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text=f'{ElectiveText.same.value[lang]} {old_teacher}', callback_data=old_teacher)
    letters = SESC_Info.TEACHER_LETTERS

    [kb.button(text=i, callback_data='letter_' + i) for i in letters]

    kb.adjust(3)
    add_back_btn(kb, lang)

    return kb.as_markup()
