from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sesc_info import SESC_Info
from tgbot.text import TEXT


def add_back_btn(keyboard: InlineKeyboardBuilder, lang: str):
    keyboard.button(text=TEXT('back', lang), callback_data='back')


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
    letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
               'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']

    [kb.button(text=i, callback_data='letter_' + i) for i in letters]
    add_back_btn(kb, lang)

    kb.adjust(3)

    return kb.as_markup()


def get_choose_teacher_kb(letter: str, lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for key, value in SESC_Info.TEACHER.items():
        if key[0] == letter:
            kb.button(text=key, callback_data=value)
    add_back_btn(kb, lang)

    kb.adjust(2)

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

    kb.adjust(1)
    return kb.as_markup()


def get_choose_auditory_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i, j in SESC_Info.AUDITORY.items():
        kb.button(text=i, callback_data=j)
    add_back_btn(kb, lang)

    kb.adjust(3)
    return kb.as_markup()


def get_choose_weekday_kb(lang: str, back: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

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


def back_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_back_btn(kb, lang)

    return kb.as_markup()


def options_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text=TEXT('free_auditory', lang), callback_data='free_auditory')
    kb.button(text=TEXT('official_site', lang), url='https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii')

    add_back_btn(kb, lang)
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
    lessons = {'Право', 'ИстФилософии', 'Информатика', 'Литература', 'ТеорПознания', 'АнглЯзык', 'Химия', 'Новейшая история', 'История', 'ЗарЛитература', 'Астрономия', 'ВсИстория', 'Алгебра', 'ХимПрактикум', 'ЭконГеография', 'География', 'Обществознание', 'Русский', 'Французский язык', 'Экономика', 'МХК', 'Музыка', 'Математика', 'Биология', 'ИстРоссии', 'Технология', 'Геометрия', 'ИнЯзык2', 'Политология', 'БиоЭлектив', 'ИМК', 'РоднЛитература', 'Физкультура', 'История русской культуры', 'РоднЯзык', 'Социология', 'АКС', 'ИнжГрафика', 'Естествознание', 'Риторика', 'Физика'}

    for i in lessons:
        kb.button(text=i, callback_data=i)

    add_back_btn(kb, lang)
    kb.adjust(3)

    return kb.as_markup()
