from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.kbd import Button

from src.database import get_async_session
from src.tgbot.settings.settings_text import SettingsText
from src.tgbot.settings.states import SettingsSG
from src.tgbot.user_models.db import DB
from src.utils.dialogs_utils import lang_getter
from src.utils.drawer_utils import render_example_image


async def style_page_changed_handler(callback: CallbackQuery, widget: ManagedScroll, dialog_manager: DialogManager, *args, **kwargs):
    try:
        style = int(callback.data.split(':')[-1])
        path = render_example_image(style)
        dialog_manager.dialog_data.update({'path_to_file': path, 'style': style})
    except Exception as e:
        print(e)


async def select_style(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    # lang = (await lang_getter(callback.from_user)).get('lang')
    async with await get_async_session() as session:
        await DB().update_user_info(session, callback.from_user.id, style=int(callback.data))

    # await dialog_manager.done()
    # await callback.message.answer(SettingsText.style_changed.value[lang])
    # await dialog_manager.start(SettingsSG.list_of_styles, mode=StartMode.RESET_STACK)
