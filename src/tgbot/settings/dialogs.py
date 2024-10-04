from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
    ScrollingGroup,
    Back,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Case

from proto import drawing_pb2
from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.settings.getters import styles_getter
from src.tgbot.settings.handlers import style_page_changed_handler, select_style
from src.tgbot.settings.settings_text import SettingsText
from src.tgbot.settings.states import SettingsSG
from src.tgbot.text import BottomMenuText
from src.utils.dialogs_utils import get_text_from_enum, lang_getter, to_main, get_text_from_text_message

router = Router()


@router.callback_query(F.data == 'go_to_settings')
async def settings_start(callback: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=SettingsSG.start)


def styles_buttons_creator():
    res = []

    for name, btn_id in drawing_pb2.Style.items():
        btn = Button(text=Const(name), id=str(btn_id), on_click=select_style)
        res.append(btn)
    return res

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
        Case(
            texts={
                1: get_text_from_enum({'ru': SettingsText.this_is_current_style.value['ru'] + SettingsText.choose_style.value['ru'],
                                        'en': SettingsText.this_is_current_style.value['en'] + SettingsText.choose_style.value['en']}),
                0: get_text_from_enum(SettingsText.choose_style.value)
            },
            selector='is_user_style'
        ),
        ScrollingGroup(
            *styles_buttons_creator(),
            width=1,
            height=1,
            id='styles',
            on_page_changed=style_page_changed_handler,
        ),
        Back(
            get_text_from_text_message('back')
        ),
        state=SettingsSG.list_of_styles,
        getter=styles_getter
    ),
)
