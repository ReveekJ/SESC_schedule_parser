from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Select,
    Button,
    Group,
    Back,
    Column,
    Multiselect,
    SwitchTo
)
from aiogram_dialog.widgets.text import Format, Case, Const

from .admin_teacher_work import save_to_dialog_data_and_next, pulpit_handler, name_input_handler, days_of_week_saver, \
    name_select_handler, switch_to_time_from_handler, old_teacher_handler, old_time_from_handler, old_time_to_handler, \
    time_handler, back_time_to_handler, back_teacher_letter_handler, cancel_elective_handler, auditory_handler, \
    back_time_from_handler, back_to_name_input, process_selfie
from .elective_text import ElectiveText, AuthText
from .getters import *
from .states import *
from ..keyboard import get_choose_schedule
from ...utils.dialogs_utils import get_text_from_enum, get_text_from_text_message


def create_old_data_button(text: dict, old_data: str, on_click, when: str = 'action_not_add') -> Button:
    return Button(
        Case(
            texts={
                'ru': text['ru'] + ' (' + Format(f'{{{old_data}}}') + ')',
                'en': text['en'] + ' (' + Format(f'{{{old_data}}}') + ')',
            },
            selector='lang'
        ),
        id=old_data,
        on_click=on_click,
        when=when
    )


def create_weekday_text() -> tuple[Case, Format]:
    return (get_text_from_enum(ElectiveText.settings_for.value),
            Format('📅 {weekday}\n'))


async def to_main(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    lang = callback.from_user.language_code
    await dialog_manager.done()
    await callback.message.edit_text(TEXT('main', lang=lang),
                                     reply_markup=get_choose_schedule(lang))


auth_dialog = Dialog(
    Window(
        get_text_from_enum(AuthText.greeting_text.value),
        MessageInput(
            func=process_selfie,
            content_types=ContentType.PHOTO
        ),
        Button(
            text=get_text_from_enum(ElectiveText.to_main.value),
            id='to_main',
            on_click=to_main
        ),  # кнопка назад сделана так, потому что остальная часть бота написана не на диалогах
        state=AuthMachine.selfie,
        getter=lang_getter
    )
)
admin_work = Dialog(
    Window(
        get_text_from_enum(ElectiveText.main_page.value),
        Button(get_text_from_enum(ElectiveText.add.value), id='add', on_click=save_to_dialog_data_and_next),
        Button(get_text_from_enum(ElectiveText.remove.value), id='remove', on_click=save_to_dialog_data_and_next),
        Button(get_text_from_enum(ElectiveText.edit_for_one_day.value),
               id='edit_for_one_day', on_click=save_to_dialog_data_and_next),
        Button(get_text_from_enum(ElectiveText.edit_permanently.value),
               id='edit_permanently', on_click=save_to_dialog_data_and_next),
        Button(
            text=get_text_from_enum(ElectiveText.to_main.value),
            id='to_main',
            on_click=to_main
        ),  # кнопка назад сделана так, потому что остальная часть бота написана не на диалогах
        state=AdminMachine.action,
        getter=lang_getter
    ),
    Window(
        get_text_from_enum(ElectiveText.choose_pulpit.value),
        Group(
            Select(
                Format('{item[1]}'),
                id='pulpit',
                item_id_getter=lambda x: str(x[0]),
                items='pulpit',
                on_click=pulpit_handler
            ),
            width=1),
        Back(
            get_text_from_text_message('back')
        ),
        getter=pulpit_getter,
        state=AdminMachine.pulpit,
    ),
    Window(
        get_text_from_enum(ElectiveText.enter_a_name.value),
        MessageInput(
            func=name_input_handler,
            content_types=ContentType.TEXT
        ),
        Back(get_text_from_text_message('back')),
        getter=lang_getter,
        state=AdminMachine.name_of_course_input
    ),
    Window(
        get_text_from_enum(ElectiveText.choose_elective.value),
        Select(
            Format('{item[1]}'),
            id='elective',
            item_id_getter=lambda x: x[1],
            items='courses',
            on_click=name_select_handler
        ),
        SwitchTo(
            text=get_text_from_text_message('back'),
            id='switch_to_pulpit',
            state=AdminMachine.pulpit
        ),
        getter=courses_by_pulpit_getter,
        state=AdminMachine.name_of_course_selector
    ),
    Window(
        get_text_from_text_message('choose_day'),
        Column(
            Multiselect(
                checked_text=Format('[✅] {item[1]}'),
                unchecked_text=Format('[ ] {item[1]}'),
                id='name',
                item_id_getter=lambda x: x[0],
                items='possible_days',
                on_state_changed=days_of_week_saver
            )
        ),
        Button(
            get_text_from_enum(ElectiveText.done.value),
            id='switch_to_time_from',
            on_click=switch_to_time_from_handler,
        ),
        Button(
            id='back_to_smth',
            text=get_text_from_text_message('back'),
            on_click=back_to_name_input
        ),
        getter=possible_days_getter,
        state=AdminMachine.day_of_week
    ),
    Window(
        *create_weekday_text(),
        get_text_from_enum(ElectiveText.time_from.value),
        Button(
            get_text_from_enum(ElectiveText.cancel_elective.value),
            id='cancel',
            on_click=cancel_elective_handler,
            when='add_cancel'
        ),
        create_old_data_button(ElectiveText.same.value, 'prev_time', old_time_from_handler, 'prev_time_exist'),
        Group(
            Select(
                Format('{item[1]}'),
                id='time_from',
                item_id_getter=lambda x: x[1],
                items='time',
                on_click=time_handler
            ),
            width=2),
        Button(
            get_text_from_text_message('back'),
            id='back_time_from',
            on_click=back_time_from_handler
        ),
        state=AdminMachine.time_from,
        getter=time_from_getter
    ),
    Window(
        *create_weekday_text(),
        get_text_from_enum(ElectiveText.time_to.value),
        create_old_data_button(ElectiveText.same.value, 'prev_time', old_time_to_handler, 'prev_time_exist'),
        Group(
            Select(
                Format('{item[1]}'),
                id='time_to',
                item_id_getter=lambda x: x[1],
                items='time',
                on_click=time_handler
            ),
            width=2),
        Back(
            get_text_from_text_message('back'),
            on_click=back_time_to_handler
        ),
        state=AdminMachine.time_to,
        getter=time_to_getter
    ),
    Window(
        *create_weekday_text(),
        get_text_from_text_message('choose_letter'),
        create_old_data_button(ElectiveText.same.value, 'old_teacher', old_teacher_handler),
        Group(
            Select(
                Format('{item[1]}'),
                id='teacher_letter',
                item_id_getter=lambda x: x[1],
                items='teacher_letter',
                on_click=save_to_dialog_data_and_next
            ),
            width=3
        ),
        Back(
            get_text_from_text_message('back'),
            on_click=back_teacher_letter_handler
        ),
        getter=teacher_letter_getter,
        state=AdminMachine.teacher_letter
    ),
    Window(
        *create_weekday_text(),
        get_text_from_text_message('choose_sub_info_teacher'),
        create_old_data_button(ElectiveText.same.value, 'old_teacher', old_teacher_handler),
        Group(
            Select(
                Format('{item[1]}'),
                id='teacher',
                item_id_getter=lambda x: x[0],
                items='teacher',
                on_click=save_to_dialog_data_and_next
            ),
            width=2
        ),
        Back(get_text_from_text_message('back')),
        getter=teacher_getter,
        state=AdminMachine.teacher
    ),
    Window(
        *create_weekday_text(),
        get_text_from_text_message('choose_sub_info_auditory'),
        create_old_data_button(ElectiveText.same.value, 'old_auditory', auditory_handler),
        Group(
            Select(
                Format('{item[1]}'),
                id='auditory',
                item_id_getter=lambda x: x[0],
                items='auditory',
                on_click=auditory_handler
            ),
            width=3
        ),
        Back(get_text_from_text_message('back')),
        getter=auditory_getter,
        state=AdminMachine.auditory
    ),
    # Window(
    #     get_text_from_enum(ElectiveText.are_you_sure.value)
    #     Button(
    #         get_text_from_enum(ElectiveText.yes.value),
    #         id='yes',
    #         on_click=,
    #     ),
    #     state
    # )
)
# TODO: сделать окно ты уверен?
