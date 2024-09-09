from aiogram_dialog.widgets.text import Case, Const

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

