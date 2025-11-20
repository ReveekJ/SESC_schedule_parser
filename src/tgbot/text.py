"""Модуль для работы с текстами через fluentogram"""
from src.tgbot.i18n import get_translator

# Маппинг старых ключей на новые (для обратной совместимости)
KEY_MAPPING = {
    'choose_role': 'choose-role',
    'choose_sub_info_group': 'choose-sub-info-group',
    'choose_sub_info_teacher': 'choose-sub-info-teacher',
    'choose_sub_info_auditory': 'choose-sub-info-auditory',
    'teacher_kb': 'teacher-kb',
    'registration_done': 'registration-done',
    'main_schedule': 'main-schedule',
    'choose_type': 'choose-type',
    'choose_day': 'choose-day',
    'no_schedule': 'no-schedule',
    'all_days': 'all-days',
    'choose_letter': 'choose-letter',
    'changed_schedule': 'changed-schedule',
    'admin_sending_message': 'admin-sending-message',
    'get_feedback': 'get-feedback',
    'feedback_done': 'feedback-done',
    'administration_role': 'administration-role',
    'optional_func': 'optional-func',
    'choose_optional_function': 'choose-optional-function',
    'free_auditory': 'free-auditory',
    'official_site': 'official-site',
    'choose_lesson': 'choose-lesson',
    'today_btn': 'today-btn',
    'bell_schedule': 'bell-schedule',
    'send_your_pass': 'send-your-pass',
    'administrator_dismissed': 'administrator-dismissed',
    'new_administrator_text': 'new-administrator-text',
    'admin_panel': 'admin-panel',
    'change_schedule': 'change-schedule',
    'reg_error': 'reg-error',
    'to_elective': 'to-elective',
    'to_feedback': 'to-feedback',
    'to_settings': 'to-settings',
    'elective_schedule': 'elective-schedule',
}

# Маппинг месяцев
MONTH_MAPPING = {
    1: 'month-january',
    2: 'month-february',
    3: 'month-march',
    4: 'month-april',
    5: 'month-may',
    6: 'month-june',
    7: 'month-july',
    8: 'month-august',
    9: 'month-september',
    10: 'month-october',
    11: 'month-november',
    12: 'month-december',
}

# Маппинг дней недели
WEEKDAY_MAPPING = {
    1: 'weekday-monday',
    2: 'weekday-tuesday',
    3: 'weekday-wednesday',
    4: 'weekday-thursday',
    5: 'weekday-friday',
    6: 'weekday-saturday',
    7: 'weekday-sunday',
}

WEEKDAY_KB_MAPPING = {
    1: 'weekday-kb-monday',
    2: 'weekday-kb-tuesday',
    3: 'weekday-kb-wednesday',
    4: 'weekday-kb-thursday',
    5: 'weekday-kb-friday',
    6: 'weekday-kb-saturday',
    7: 'weekday-kb-sunday',
}


def TEXT(short_name: str, lang: str = 'ru'):
    """
    Получить текст по ключу и языку.
    Обратная совместимость со старым API.
    """
    translator = get_translator(lang)
    
    # Обработка специальных случаев
    if short_name == 'month':
        return [translator.get(MONTH_MAPPING[i]) for i in range(1, 13)]
    
    if short_name == 'weekdays':
        return {i: translator.get(WEEKDAY_MAPPING[i]) for i in range(1, 8)}
    
    if short_name == 'weekdays_kb':
        return {i: translator.get(WEEKDAY_KB_MAPPING[i]) for i in range(1, 8)}
    
    # Обычный ключ
    key = KEY_MAPPING.get(short_name, short_name.replace('_', '-'))
    try:
        return translator.get(key)
    except Exception:
        # Fallback на старый ключ если не найден
        return translator.get(short_name.replace('_', '-'))


# Для обратной совместимости с BottomMenuText
class _BottomMenuText:
    """Класс для текстов нижнего меню"""
    @staticmethod
    def _get_value(key: str, lang: str):
        translator = get_translator(lang)
        key_mapping = {
            'optional': 'bottom-menu-optional',
            'electives': 'bottom-menu-electives',
            'to_main': 'bottom-menu-to-main',
        }
        return translator.get(key_mapping.get(key, key))
    
    @staticmethod
    def _get_all_languages_value(key: str):
        """Получить значение для всех поддерживаемых языков"""
        from src.tgbot.i18n import supported_locales
        return {lang: _BottomMenuText._get_value(key, lang) for lang in supported_locales}
    
    @property
    def optional(self):
        class _Optional:
            @property
            def value(self):
                return _BottomMenuText._get_all_languages_value('optional')
        return _Optional()
    
    @property
    def electives(self):
        class _Electives:
            @property
            def value(self):
                return _BottomMenuText._get_all_languages_value('electives')
        return _Electives()
    
    @property
    def to_main(self):
        class _ToMain:
            @property
            def value(self):
                return _BottomMenuText._get_all_languages_value('to_main')
        return _ToMain()


BottomMenuText = _BottomMenuText()
