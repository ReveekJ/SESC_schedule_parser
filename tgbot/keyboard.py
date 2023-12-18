from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.text import TEXT
from sesc_info import SESC_Info


def get_choose_role_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('student', lang), callback_data='group')
    kb.button(text=TEXT('teacher', lang), callback_data='teacher')
    # The Illusion of choice
    kb.button(text=TEXT('parent', lang), callback_data='group')

    kb.adjust(1)

    return kb.as_markup()


def get_choose_group_kb(lang: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    groups = SESC_Info.GROUP

    for i in groups.keys():
        kb.button(text=i, callback_data=groups[i])

    kb.adjust(3)

    return kb.as_markup()


# Должно принимать lang для того чтобы работал allSchedule
def get_choose_teacher_kb(lang: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    groups = SESC_Info.TEACHER

    for i in groups.keys():
        kb.button(text=i, callback_data=groups[i])

    kb.adjust(2)

    return kb.as_markup()


def get_choose_schedule(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('today', lang), callback_data='today')
    kb.button(text=TEXT('tomorrow', lang), callback_data='tomorrow')
    kb.button(text=TEXT('all_days', lang), callback_data='all_days')
    kb.button(text=TEXT('all', lang), callback_data='see_all')
    kb.adjust(1)
    return kb.as_markup()


# TODO: translate into English
def get_choose_type_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i, j in SESC_Info.TYPE.items():
        kb.button(text=i, callback_data='type_' + j)

    kb.adjust(1)
    return kb.as_markup()


def get_choose_auditory_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i, j in SESC_Info.AUDITORY.items():
        kb.button(text=i, callback_data=j)

    kb.adjust(3)
    return kb.as_markup()


def get_choose_weekday_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for callback_data, text in TEXT('weekdays', lang).items():
        if callback_data == 7:
            continue

        kb.button(text=text, callback_data=str(callback_data))

    kb.adjust(1)
    return kb.as_markup()
