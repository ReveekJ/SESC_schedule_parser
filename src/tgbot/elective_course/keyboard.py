import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.keyboard import add_back_btn
from src.tgbot.text import TEXT
from src.tgbot.sesc_info import SESC_Info


def get_elective_course_main_page_admin_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ElectiveText.add.value[lang], callback_data='add')
    kb.button(text=ElectiveText.remove.value[lang], callback_data='remove')

    return kb.as_markup()


def get_elective_course_main_page_user_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('today', lang), callback_data='today_elective_course')
    kb.button(text=TEXT('tomorrow', lang), callback_data='tomorrow_elective_course')
    kb.button(text=TEXT('all_days', lang), callback_data='all_days_elective_course')
    kb.button(text=ElectiveText.register_to_new_course.value[lang], callback_data='register_to_new_course')
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


def get_elective_kb(lang: str, courses: list[ElectiveCourse]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i in courses:
        kb.button(text=i.subject, callback_data=i.id)

    kb.adjust(2)
    add_back_btn(kb, lang)
    return kb.as_markup()
