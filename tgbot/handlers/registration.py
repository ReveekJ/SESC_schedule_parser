from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from models.db import DB
from tgbot.text import TEXT
from tgbot.keyboard import get_choose_role_kb, get_choose_group_kb, get_choose_teacher_kb


class Form(StatesGroup):
    role = State()
    sub_info = State()
    lang = State()


router = Router()


@router.message(CommandStart())
async def start_registration(message: Message, state: FSMContext) -> None:
    lang = message.from_user.language_code
    await state.update_data(lang=lang)

    await state.set_state(Form.role)
    await message.answer(TEXT('hello', lang=lang),
                         disable_notification=True)

    await message.answer(TEXT('choose_role', lang=lang),
                         reply_markup=get_choose_role_kb(lang),
                         disable_notification=True)


@router.callback_query(Form.role, F.data.casefold() == 'student')
async def set_role_student(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('lang')

    await state.update_data(role=callback.data)
    await state.set_state(Form.sub_info)

    await callback.message.delete()
    await callback.message.answer(TEXT('choose_sub_info_student', lang=lang),
                                  reply_markup=get_choose_group_kb(),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(Form.role, F.data.casefold() == 'teacher')
async def set_role_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('lang')

    await state.update_data(role=callback.data)
    await state.set_state(Form.sub_info)

    await callback.message.delete()
    await callback.message.answer(TEXT('choose_sub_info_teacher', lang=lang),
                                  reply_markup=get_choose_teacher_kb(),
                                  disable_notification=True)

    await callback.answer()


@router.callback_query(Form.sub_info)
async def set_sub_role_student(callback: CallbackQuery, state: FSMContext):
    session = DB()
    await session.connect()

    data = await state.get_data()
    # print(data)
    role = data['role']
    sub_role = callback.data
    lang = data['lang']
    chat_id = callback.from_user.id

    await session.create_user(id=str(chat_id),
                              role=role,
                              sub_info=sub_role,
                              lang=lang)

    # TODO: send main page

    await callback.answer()
