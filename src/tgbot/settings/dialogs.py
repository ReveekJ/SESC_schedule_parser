from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo, ScrollingGroup
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const

from src.tgbot.settings.getters import styles_getter
from src.tgbot.settings.handlers import style_page_changed_handler
from src.tgbot.settings.settings_text import SettingsText
from src.tgbot.settings.states import SettingsSG
from src.utils.dialogs_utils import get_text_from_enum, lang_getter

router = Router()


@router.message(Command('settings'))
async def settings_start(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(state=SettingsSG.start)


dialog = Dialog(
    Window(
        get_text_from_enum(SettingsText.settings_header.value),
        SwitchTo(
            get_text_from_enum(SettingsText.change_style.value),
            id='change_style',
            state=SettingsSG.list_of_styles
        ),
        getter=lang_getter,
        state=SettingsSG.start
    ),
    Window(
        DynamicMedia('example'),
        Const('how_are_u'),
        ScrollingGroup(
            Button(Const('hello'), id='hello'),
            Button(Const('ajghsf'), id='ajghsf'),
            Button(Const('ajasdfgghsf'), id='sdfgsdfg'),
            width=1,
            height=1,
            id='styles',
            on_page_changed=style_page_changed_handler,
        ),
        state=SettingsSG.list_of_styles,
        getter=styles_getter
    )
    # Window(
    #     get_text_from_enum(SettingsText.choose_style.value),
    #     Group(
    #         Select(
    #             Format('{item[1]}'),
    #             item_id_getter=lambda x: str(x[0]),
    #             items='styles',
    #             id='style_select',
    #             on_click=style_show_handler,
    #         ),
    #         width=2
    #     ),
    #     Back(
    #         get_text_from_text_message('back')
    #     ),
    #     state=SettingsSG.list_of_styles,
    #     getter=styles_getter
    # ),
    # Window(
    #     DynamicMedia('photo'),
    #     # get_text_from_enum(SettingsText.its_okay.value),
    #     getter=example_photo_getter,
    #     state=SettingsSG.is_it_okay
    # )
)