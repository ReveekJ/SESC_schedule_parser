import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.tgbot.sesc_info import SESC_Info
from src.tgbot.elective_course.elective_text import ELECTIVE_TEXT


def get_elective_course_main_page_admin_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ELECTIVE_TEXT('add', lang), callback_data='add')
    kb.button(text=ELECTIVE_TEXT('remove', lang), callback_data='remove')

    return kb.as_markup()


def get_elective_course_main_page_user_kb(lang: str) -> InlineKeyboardMarkup:
    pass
