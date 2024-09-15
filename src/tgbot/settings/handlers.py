from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll

from src.utils.drawer_utils import render_example_image


async def style_page_changed_handler(callback: CallbackQuery, widget: ManagedScroll, dialog_manager: DialogManager, *args, **kwargs):
    path = render_example_image(int(callback.data.split(':')[-1]))
    dialog_manager.dialog_data.update({'path_to_file': path})
