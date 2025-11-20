"""Модуль для работы с текстами настроек через fluentogram"""
from src.tgbot.i18n import get_translator


class SettingsText:
    """Класс для текстов настроек"""
    
    @staticmethod
    def _get_value(key: str, lang: str):
        translator = get_translator(lang)
        key_mapping = {
            'settings_header': 'settings-header',
            'change_style': 'settings-change-style',
            'choose_style': 'settings-choose-style',
            'this_is_current_style': 'settings-this-is-current-style',
            'style_changed': 'settings-style-changed',
        }
        return translator.get(key_mapping.get(key, key))
    
    def __getattr__(self, name):
        """Динамическое создание свойств для обратной совместимости"""
        class _TextValue:
            @property
            def value(self):
                return {
                    'ru': SettingsText._get_value(name, 'ru'),
                    'en': SettingsText._get_value(name, 'en'),
                }
        return _TextValue()


# Создаем экземпляр для обратной совместимости
SettingsText = SettingsText()
