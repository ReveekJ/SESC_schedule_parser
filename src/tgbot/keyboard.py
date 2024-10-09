import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, ButtonType

from src.tgbot.sesc_info import SESC_Info
from src.tgbot.text import TEXT, BottomMenuText


def add_back_btn(keyboard: InlineKeyboardBuilder, lang: str):
    keyboard.row(InlineKeyboardButton(text=TEXT('back', lang), callback_data='back'), width=1)


def admin_functions(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT("change_schedule", lang), callback_data="change_schedule")
    return kb.as_markup()


def bottom_menu(lang: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(
            text=BottomMenuText.electives.value
        ),
        KeyboardButton(
            text=BottomMenuText.optional.value
        )
    )
    kb.row(
        KeyboardButton(
            text=BottomMenuText.feedback.value
        ),
        KeyboardButton(
            text=BottomMenuText.settings.value
        )
    )
    # KeyboardButton(text=BottomMenuText.settings.value)
    kb.row(KeyboardButton(text=BottomMenuText.to_main.value))

    return kb.as_markup(resize_keyboard=True)


def get_choose_role_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('student', lang), callback_data='group')
    kb.button(text=TEXT('teacher', lang), callback_data='teacher')
    # The Illusion of choice
    kb.button(text=TEXT('parent', lang), callback_data='group')
    # kb.button(text=TEXT('administration_role', lang), callback_data='administration')

    kb.adjust(1)

    return kb.as_markup()


def get_choose_group_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    groups = SESC_Info.GROUP

    for i in groups.keys():
        kb.button(text=i, callback_data=groups[i])
    add_back_btn(kb, lang)

    kb.adjust(3)
    return kb.as_markup()


def get_letter_of_teacher_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    letters = SESC_Info.TEACHER_LETTERS

    for i in range(0, min(len(letters), len(letters) - (len(letters) % 3)), 3):
        kb.row(*[InlineKeyboardButton(text=letters[i + j], callback_data='letter_' + letters[i + j])
                 for j in range(3)], width=3)

    if len(letters) % 3 != 0:
        kb.row(*[InlineKeyboardButton(text=letters[-i - 1], callback_data='letter_' + letters[-i - 1]) for
                 i in range(len(letters) % 3 + 1, -1, -1)], width=3)

    add_back_btn(kb, lang)

    return kb.as_markup(row_width=3)


def get_choose_teacher_kb(letter: str, lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for key, value in SESC_Info.TEACHER.items():
        if key[0] == letter:
            kb.button(text=key, callback_data=value)

    kb.adjust(2)
    add_back_btn(kb, lang)

    return kb.as_markup()


def get_choose_schedule(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('today', lang), callback_data='today')
    kb.button(text=TEXT('tomorrow', lang), callback_data='tomorrow')
    kb.button(text=TEXT('all_days', lang), callback_data='all_days')

    for i, j in SESC_Info.TYPE.items():
        # ignore all schedule
        if j in ['all']:
            continue
        # если это преподаватель, то берем специальный текст, так как мы имеем похожий текст при регистрации с этим
        # short_name
        kb.button(text=TEXT(j, lang) if j != 'teacher' else TEXT('teacher_kb', lang), callback_data='type_' + j)

    # kb.button(text=TEXT('to_elective', lang), callback_data='to_elective')  эта кнопка перенесена на другую клавиатуру
    kb.adjust(1)
    return kb.as_markup()


def get_choose_auditory_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i, j in SESC_Info.AUDITORY.items():
        kb.button(text=i, callback_data=j)

    kb.adjust(3)
    add_back_btn(kb, lang)

    return kb.as_markup()


def get_choose_weekday_kb(lang: str, back: bool = True, today_btn: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if today_btn:
        today = datetime.date.today().weekday() + 1
        kb.button(text=TEXT('today_btn', lang), callback_data=str(today if today != 7 else 1))

    for callback_data, text in TEXT('weekdays_kb', lang).items():
        if callback_data == 7:
            continue

        kb.button(text=text, callback_data=str(callback_data))

    if back:
        add_back_btn(kb, lang)

    kb.adjust(1)
    return kb.as_markup()


def hard_choice(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('yes', lang), callback_data='relogin')
    kb.button(text=TEXT('no', lang), callback_data='reloginf')
    return kb.as_markup()


def aprove(lang: str, user_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXT('yes', lang), callback_data='adminNew_' + user_id + '_yes')
    kb.button(text=TEXT('no', lang), callback_data='adminNew_' + user_id + '_no')
    return kb.as_markup()


def back_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_back_btn(kb, lang)

    return kb.as_markup()


def options_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text=TEXT('free_auditory', lang), callback_data='free_auditory')
    kb.button(text=TEXT('bell_schedule', lang), callback_data='bell_schedule')
    kb.button(text=TEXT('relogin', lang), callback_data='to_relogin')
    kb.button(text=TEXT('official_site', lang), url='https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii')

    kb.adjust(1)

    return kb.as_markup()


def choose_lessons_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i in range(1, 8):
        kb.button(text=str(i) + ' ' + TEXT('lesson', lang), callback_data=str(i))

    add_back_btn(kb, lang)
    kb.adjust(1)

    return kb.as_markup()


def all_lessons_kb(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    lessons = {'Право', 'ИстФилософии', 'Информатика', 'Литература', 'ТеорПознания', 'АнглЯзык', 'Химия',
               'Новейшая история', 'История', 'ЗарЛитература', 'Астрономия', 'ВсИстория', 'Алгебра', 'ХимПрактикум',
               'ЭконГеография', 'География', 'Обществознание', 'Русский', 'Французский язык', 'Экономика', 'МХК',
               'Музыка', 'Математика', 'Биология', 'ИстРоссии', 'Технология', 'Геометрия', 'ИнЯзык2', 'Политология',
               'БиоЭлектив', 'ИМК', 'РоднЛитература', 'Физкультура', 'История русской культуры', 'РоднЯзык',
               'Социология', 'АКС', 'ИнжГрафика', 'Естествознание', 'Риторика', 'Физика'}

    for i in lessons:
        kb.button(text=i, callback_data=i)

    kb.adjust(3)
    add_back_btn(kb, lang)

    return kb.as_markup()
