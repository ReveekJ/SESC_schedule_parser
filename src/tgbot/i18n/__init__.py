from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

# Путь к директории с переводами
I18N_DIR = Path(__file__).parent.resolve()


def _load_ftl_file(locale: str) -> str:
    """Загрузить содержимое .ftl файла для указанной локали"""
    ftl_path = I18N_DIR / locale / "main.ftl"
    if not ftl_path.exists():
        raise FileNotFoundError(f"Translation file not found: {ftl_path}")
    return ftl_path.read_text(encoding="utf-8")


# Создаем переводчики для каждой локали
translators = []
# Маппинг локалей на правильные форматы для babel
locale_formats = {
    "ru": "ru-RU",
    "en": "en-US",
    "pl": "pl-PL",
    "de": "de-DE",
    "he": "he-IL",
    "cs": "cs-CZ",
    "zh": "zh-CN",
    "ko": "ko-KR",
    "ja": "ja-JP",
    "ar": "ar-SA"
}

# Список всех поддерживаемых локалей
supported_locales = ["ru", "en", "pl", "de", "he", "cs", "zh", "ko", "ja", "ar"]

for locale in supported_locales:
    try:
        ftl_content = _load_ftl_file(locale)
        bundle = FluentBundle.from_string(
            locale_formats[locale],
            ftl_content,
            use_isolating=False
        )
        translators.append(
            FluentTranslator(
                locale=locale,
                translator=bundle
            )
        )
    except Exception as e:
        # Если не удалось загрузить файл, создаем пустой bundle
        print(f"Warning: Failed to load translations for {locale}: {e}")
        bundle = FluentBundle.from_string(
            locale_formats[locale],
            "",
            use_isolating=False
        )
        translators.append(
            FluentTranslator(
                locale=locale,
                translator=bundle
            )
        )

# Маппинг локалей с fallback
# Если перевод не найден для текущей локали, используется fallback
# Для всех языков fallback на русский (кроме русского, который fallback на английский)
locales_map = {
    "ru": ("ru", "en"),
    "en": ("en", "ru"),
    "pl": ("pl", "ru"),
    "de": ("de", "ru"),
    "he": ("he", "ru"),
    "cs": ("cs", "ru"),
    "zh": ("zh", "ru"),
    "ko": ("ko", "ru"),
    "ja": ("ja", "ru"),
    "ar": ("ar", "ru"),
}

# Создаем TranslatorHub
# root_locale - язык по умолчанию, используется когда перевод не найден
hub = TranslatorHub(
    locales_map=locales_map,
    translators=translators,
    root_locale="ru",  # Русский как язык по умолчанию
)


def get_translator(locale: str = "ru"):
    """Получить переводчик для указанной локали"""
    # Нормализуем локаль
    if locale not in supported_locales:
        locale = "ru"  # Fallback на русский по умолчанию
    return hub.get_translator_by_locale(locale)
