"""Модуль для работы с текстами факультативов через fluentogram"""
from src.tgbot.i18n import get_translator


class ElectiveText:
    """Класс для текстов факультативов"""
    
    @staticmethod
    def _get_value(key: str, lang: str):
        translator = get_translator(lang)
        key_mapping = {
            'add': 'elective-add',
            'remove': 'elective-remove',
            'edit_permanently': 'elective-edit-permanently',
            'edit_for_one_day': 'elective-edit-for-one-day',
            'to_main': 'elective-to-main',
            'main_page': 'elective-main-page',
            'register_to_new_course': 'elective-register-to-new-course',
            'choose_pulpit': 'elective-choose-pulpit',
            'choose_elective': 'elective-choose-elective',
            'successfully_sub_or_unsub': 'elective-successfully-sub-or-unsub',
            'unsubscribe': 'elective-unsubscribe',
            'enter_a_name': 'elective-enter-a-name',
            'are_you_sure_remove': 'elective-are-you-sure-remove',
            'yes': 'elective-yes',
            'no': 'elective-no',
            'remove_done': 'elective-remove-done',
            'done': 'elective-done',
            'time_from': 'elective-time-from',
            'time_to': 'elective-time-to',
            'cancel_elective': 'elective-cancel',
            'error': 'elective-error',
            'same': 'elective-same',
            'same_name_already_exist': 'elective-same-name-already-exist',
            'settings_for': 'elective-settings-for',
            'elective_changes': 'elective-changes',
            'loading': 'elective-loading',
        }
        return translator.get(key_mapping.get(key, key))
    
    def __getattr__(self, name):
        """Динамическое создание свойств для обратной совместимости"""
        class _TextValue:
            @property
            def value(self):
                return {
                    'ru': ElectiveText._get_value(name, 'ru'),
                    'en': ElectiveText._get_value(name, 'en'),
                }
        return _TextValue()


class AuthText:
    """Класс для текстов авторизации"""
    
    @staticmethod
    def _get_value(key: str, lang: str):
        translator = get_translator(lang)
        key_mapping = {
            'greeting_text': 'auth-greeting-text',
            'approve_btn': 'auth-approve-btn',
            'decline_btn': 'auth-decline-btn',
            'wait_pls': 'auth-wait-pls',
            'you_approved': 'auth-you-approved',
            'you_declined': 'auth-you-declined',
        }
        return translator.get(key_mapping.get(key, key))
    
    def __getattr__(self, name):
        """Динамическое создание свойств для обратной совместимости"""
        class _TextValue:
            @property
            def value(self):
                return {
                    'ru': AuthText._get_value(name, 'ru'),
                    'en': AuthText._get_value(name, 'en'),
                }
        return _TextValue()


# Создаем экземпляры для обратной совместимости
ElectiveText = ElectiveText()
AuthText = AuthText()
