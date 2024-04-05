from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, FSInputFile, Message

from src.tgbot.auxiliary import Form, bot
from src.tgbot.auxiliary import send_schedule
from src.tgbot.main_work.registration import func_start_registration
from src.tgbot.keyboard import (get_choose_group_kb, get_choose_weekday_kb, get_choose_auditory_kb,
                                get_choose_teacher_kb, get_choose_schedule, get_letter_of_teacher_kb)
from src.tgbot.parser import PARSER
from src.tgbot.sesc_info import SESC_Info
from src.tgbot.text import TEXT


class AddCourseMachine(Form):
    pass


router = Router()


async def add_course_func(callback_of_message: CallbackQuery | Message, state):
    pass
