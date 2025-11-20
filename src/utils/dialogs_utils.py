from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Multiselect, ManagedMultiselect
from aiogram_dialog.widgets.text import Case, Const

from src.database import get_async_session
from src.tgbot.i18n import get_translator
from src.tgbot.keyboard import get_choose_schedule
from src.tgbot.text import TEXT
from src.tgbot.user_models.db import DB


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
    """Получить язык пользователя из БД"""
    from src.tgbot.i18n import supported_locales
    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, event_from_user.id)
        if user and user.lang:
            return {'lang': user.lang}
    # Fallback на language_code если пользователь не найден
    lang = event_from_user.language_code or 'ru'
    # Нормализуем код языка (например, 'pl-PL' -> 'pl')
    if lang and '-' in lang:
        lang = lang.split('-')[0]
    if lang not in supported_locales:
        lang = 'ru'
    return {'lang': lang}


async def to_main(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Вернуться на главную страницу"""
    from src.tgbot.i18n import supported_locales
    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, callback.from_user.id)
        if user and user.lang:
            lang = user.lang
        else:
            lang = callback.from_user.language_code or 'ru'
            # Нормализуем код языка (например, 'pl-PL' -> 'pl')
            if lang and '-' in lang:
                lang = lang.split('-')[0]
            if lang not in supported_locales:
                lang = 'ru'
    await dialog_manager.done()
    await callback.message.edit_text(TEXT('main', lang=lang),
                                     reply_markup=get_choose_schedule(lang))


#  узкая функция, но часто используется
def get_days_of_week(multiselect_name: str, dialog_manager: DialogManager) -> list[int]:
    days_multiselect: ManagedMultiselect = dialog_manager.find(multiselect_name)
    checked = days_multiselect.get_checked()

    if not checked:
        checked = dialog_manager.dialog_data.get('days_of_week') if dialog_manager.dialog_data.get('days_of_week') else []

    dialog_manager.dialog_data.update({'days_of_week': checked})  # фиксит легаси получение days_of_week

    return checked
