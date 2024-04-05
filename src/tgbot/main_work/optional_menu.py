from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, FSInputFile

from config import PATH_TO_PROJECT
from src.tgbot.auxiliary import Form, bot
from src.tgbot.main_work.registration import func_start_registration
from src.tgbot.keyboard import (get_choose_schedule,
                                options_kb, get_choose_weekday_kb, choose_lessons_kb)
from src.tgbot.parser import PARSER
from src.tgbot.text import TEXT

router = Router()


class FreeAuditoryMachine(Form):
    weekday_for_free_auditory = State()
    lesson_for_free_auditory = State()


@router.message(Command('optional'))
async def optional_func(message: Message | CallbackQuery, state: FSMContext):
    lang = message.from_user.language_code

    await state.clear()
    await state.update_data(prev=func_start_registration)

    # произойдет в том случае, если нажали на кнопку назад
    if isinstance(message, CallbackQuery):
        chat_id = message.message.chat.id
        message_id = message.message.message_id

        await bot.edit_message_text(text=TEXT('choose_optional_function', lang),
                                    chat_id=chat_id,
                                    message_id=message_id,
                                    reply_markup=options_kb(lang))
        await message.answer()
    else:
        chat_id = message.chat.id

        await message.delete()
        await bot.send_message(text=TEXT('choose_optional_function', lang),
                               chat_id=chat_id,
                               reply_markup=options_kb(lang))


@router.callback_query(F.data == 'free_auditory')
async def free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(prev=optional_func)
    await state.set_state(FreeAuditoryMachine.weekday_for_free_auditory)

    await bot.edit_message_text(text=TEXT('choose_day', lang),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=get_choose_weekday_kb(lang))
    await callback.answer()


@router.callback_query(FreeAuditoryMachine.weekday_for_free_auditory)
async def weekday_for_free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(weekday_for_free_auditory=callback.data)
    await state.set_state(FreeAuditoryMachine.lesson_for_free_auditory)
    await state.update_data(prev=free_auditory)

    await bot.edit_message_text(text=TEXT('choose_lesson', lang),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=choose_lessons_kb(lang))

    await callback.answer()


@router.callback_query(FreeAuditoryMachine.lesson_for_free_auditory)
async def send_free_auditory(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code

    await state.update_data(lesson_for_free_auditory=callback.data)
    data = await state.get_data()
    await state.clear()

    free = await PARSER.get_free_auditories(int(data.get('weekday_for_free_auditory')),
                                            int(data.get('lesson_for_free_auditory')))
    separator = ' | '  # разделитель между цифрами
    free_on_one_line = 6  # кол-во чисел на одной строчке
    free_str = ''  # итоговая строчка, которую будем отправлять

    for num, lesson in enumerate(free):
        if num % free_on_one_line == 0:
            free_str += '\n'
        free_str += lesson + separator

    free_str = free_str[:-len(separator)]  # обрезаем последний separator

    await bot.edit_message_text(text=free_str,
                                chat_id=chat_id,
                                message_id=message_id)

    # отправка основного сообщения
    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)
    await callback.answer()


@router.callback_query(F.data == 'bell_schedule')
async def bell_schedule(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    lang = callback.from_user.language_code
    path = PATH_TO_PROJECT + 'schedules/bell_schedule.png'

    await bot.delete_message(chat_id, message_id)
    await bot.send_photo(chat_id=chat_id,
                         photo=FSInputFile(path),
                         disable_notification=True)
    await callback.message.answer(TEXT('main', lang),
                                  reply_markup=get_choose_schedule(lang),
                                  disable_notification=True)

    await callback.answer()
