from aiogram.enums import ContentType
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment

from proto.drawing_pb2 import Style
from src.database import get_async_session
from src.tgbot.user_models.db import DB
from src.utils.dialogs_utils import lang_getter, __list_to_select_format
from src.utils.drawer_utils import render_example_image


async def styles_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
    lang = (await lang_getter(event_from_user)).get('lang')
    path = dialog_manager.dialog_data.get('path_to_file')

    if path is None:  # когда юзер в первый раз открыл меню с выбором темы
        async with await get_async_session() as session:
            user = await DB().select_user_by_id(session, event_from_user.id)
            path = render_example_image(user.style)

    image = MediaAttachment(ContentType.PHOTO, path=path)

    return {'lang': lang,
            'styles': __list_to_select_format(Style.keys(), Style.values()),
            'example': image}


# async def example_photo_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs) -> dict:
#     lang = (await lang_getter(event_from_user)).get('lang')
#     image = MediaAttachment(ContentType.PHOTO, path=dialog_manager.dialog_data.get('path_to_file'))
#
#     return {'lang': lang,
#             'photo': image}
