from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Case, Const

from src.tgbot.keyboard import get_choose_schedule
from src.tgbot.text import TEXT


def get_text_from_enum(text: dict[str, str]) -> Case:
    return Case(
        texts={
            'ru': Const(text.get('ru')),
            'en': Const(text.get('en')),
        },
        selector='lang'
    )


def get_text_from_text_message(short_name) -> Case:
    return Case(
        texts={
            'ru': Const(TEXT(short_name, 'ru')),
            'en': Const(TEXT(short_name, 'en')),
        },
        selector='lang'
    )


def __list_to_select_format(items: list, custom_index: list | None = None) -> list[tuple]:
    return [(index, elem) for index, elem in zip(range(len(items)) if custom_index is None else custom_index, items)]


async def lang_getter(event_from_user: User, **kwargs) -> dict:
    return {'lang': event_from_user.language_code}


async def to_main(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    lang = callback.from_user.language_code
    await dialog_manager.done()
    await callback.message.edit_text(TEXT('main', lang=lang),
                                     reply_markup=get_choose_schedule(lang))
