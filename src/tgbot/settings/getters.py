from pprint import pprint

from aiogram.enums import ContentType
from aiogram.types import User, Update
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.common import ManagedScroll

from proto.drawing_pb2 import Style
from src.database import get_async_session
from src.tgbot.user_models.db import DB
from src.utils.dialogs_utils import lang_getter, __list_to_select_format
from src.utils.drawer_utils import render_example_image


async def styles_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')

    async with await get_async_session() as session:
        user = await DB().select_user_by_id(session, event_from_user.id)

    path = dialog_manager.dialog_data.get('path_to_file', render_example_image(user.style))
    style = dialog_manager.dialog_data.get('style', user.style)
    image = MediaAttachment(ContentType.PHOTO, path=path)


    # выставляем верную страницу и сохраняем id сообщения
    if dialog_manager.dialog_data.get('is_first_entry') is None:
        dialog_manager.dialog_data['is_first_entry'] = True
        scroll = dialog_manager.find('styles')
        await scroll.set_page(int(style))

        await DB().update_last_message_id(event_from_user.id, user.last_message_id + 1)

    return {'lang': lang, # __list_to_select_format(Style.keys(), Style.values()),
            'is_user_style': user.style == style,
            'example': image}
