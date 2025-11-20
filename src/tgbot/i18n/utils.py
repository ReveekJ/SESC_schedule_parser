"""Утилиты для работы с локализацией"""
from typing import Optional

from src.tgbot.i18n import get_translator
from src.tgbot.user_models.db import DB
from src.database import get_async_session


async def get_user_translator(user_id: Optional[int] = None, lang: Optional[str] = None):
    """
    Получить переводчик для пользователя.
    
    Args:
        user_id: ID пользователя (если None, используется lang)
        lang: Язык напрямую (если None, берется из БД по user_id)
    
    Returns:
        Переводчик fluentogram
    """
    if lang:
        return get_translator(lang)
    
    if user_id:
        async with await get_async_session() as session:
            user = await DB().select_user_by_id(session, user_id)
            if user and user.lang:
                return get_translator(user.lang)
    
    # По умолчанию русский
    return get_translator("ru")


def get_translator_by_lang(lang: str):
    """Получить переводчик по языку"""
    return get_translator(lang)



