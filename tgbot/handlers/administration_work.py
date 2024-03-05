from typing import Any

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from tgbot.handlers.auxiliary import Form, bot
from tgbot.handlers.registration import func_start_registration
from tgbot.keyboard import (get_choose_schedule, get_choose_weekday_kb, get_choose_group_kb, choose_lessons_kb,
                            all_lessons_kb, get_letter_of_teacher_kb,
                            get_choose_teacher_kb, get_choose_auditory_kb)
from tgbot.text import TEXT

router = Router()


class AdministrationWorkMachine(Form):
    change_day = State()
    change_group = State()
    change_num_lesson = State()
    to_lesson = State()
    to_teacher_first_letter = State()
    to_teacher = State()
    to_auditory = State()

    __dict_of_next_states = {'AdministrationWorkMachine:change_day': change_group,
                             'AdministrationWorkMachine:change_group': change_num_lesson,
                             'AdministrationWorkMachine:change_num_lesson': to_lesson,
                             'AdministrationWorkMachine:to_lesson': to_teacher_first_letter,
                             'AdministrationWorkMachine:to_teacher_first_letter': to_teacher,
                             'AdministrationWorkMachine:to_teacher': to_auditory}

    @classmethod
    def get_next_state(cls, state: str):
        return cls.__dict_of_next_states[state]

    @classmethod
    def state_to_func(cls, lang: str, chat_id: int, message_id: int, state: str, letter_of_teacher: str = 'А') -> (
            list[dict[str, int | InlineKeyboardMarkup | Any] | Any] |
            list[dict[str, int | InlineKeyboardMarkup | Any] | Any]):
        state_to_func = {
            cls.change_day.state: [bot.edit_message_text, {
                'text': TEXT('choose_day', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': get_choose_weekday_kb(lang)
            }],
            cls.change_group.state: [bot.edit_message_text, {
                'text': TEXT('choose_sub_info_group', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': get_choose_group_kb(lang)
            }],
            cls.change_num_lesson.state: [bot.edit_message_text, {
                'text': TEXT('choose_lesson', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': choose_lessons_kb(lang)
            }],
            cls.to_lesson.state: [bot.edit_message_text, {
                'text': TEXT('choose_lesson', lang),  # TODO: текст
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': all_lessons_kb(lang)
            }],
            cls.to_teacher_first_letter.state: [bot.edit_message_text, {
                'text': TEXT('choose_sub_info_teacher', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': get_letter_of_teacher_kb(lang)
            }],
            cls.to_teacher.state: [bot.edit_message_text, {
                'text': TEXT('choose_sub_info_teacher', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': get_choose_teacher_kb(letter_of_teacher, lang)
            }],
            cls.to_auditory.state: [bot.edit_message_text, {
                'text': TEXT('choose_sub_info_auditory', lang),
                'chat_id': chat_id,
                'message_id': message_id,
                'reply_markup': get_choose_auditory_kb(lang)
            }]
        }

        return state_to_func[state]


@router.callback_query(AdministrationWorkMachine.to_auditory)
async def to_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    data = await state.get_data()
    await state.clear()

    # TODO: работа с api
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=TEXT('main', lang=lang),
                                reply_markup=get_choose_schedule(lang))
    await callback.answer()


@router.callback_query(F.data == 'change_schedule')
@router.callback_query(StateFilter(AdministrationWorkMachine))
async def start_administration_work(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    current_state = await state.get_state()

    #  обновляем данные в FSM
    if current_state is not None:
        await state.update_data(**{current_state: callback.data})

    if current_state is None:
        await state.update_data(prev=func_start_registration)  # TODO: функция main_page от администрации

    try:
        if current_state is None:
            raise ValueError('Invalid state')
        #  выбираем следующий стейт
        await state.set_state(AdministrationWorkMachine.get_next_state(current_state))
    except ValueError as e:
        #  если не получилось, значит сейчас стейта никакого нет, значит нужно установить на первый стейт
        #  а если это последний стейт, то он отловится на хендлере выше
        await state.set_state(AdministrationWorkMachine.change_day)
    except Exception as e:
        print('err', e)

    next_state = await state.get_state()
    print('2', current_state)

    # получаем и исполняем нужную функцию
    if next_state == AdministrationWorkMachine.to_teacher.state:
        letter = await state.get_data()
        print(letter)
        letter = letter[current_state].split('_')[-1]
        func = AdministrationWorkMachine.state_to_func(lang, chat_id, message_id, next_state, letter)
    else:
        func = AdministrationWorkMachine.state_to_func(lang, chat_id, message_id, next_state)

    await func[0](**func[1])
    await callback.answer()
