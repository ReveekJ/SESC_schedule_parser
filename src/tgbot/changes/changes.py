import asyncio
import logging

from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import FSInputFile

from src.database import get_async_session
from src.tgbot.auxiliary import send_schedule
from src.tgbot.parser import PARSER
from src.tgbot.user_models.db import DB


async def sending_schedule_changes():
    # получаем измения
    logging.debug('начинаю проверку изменений')
    changes = await PARSER.check_for_changes()
    logging.debug('получил изменения')

    for elem in changes:
        role = elem.type
        sub_info = elem.second
        weekday = elem.weekday
        # schedule = elem.schedule

        async with await get_async_session() as session:
            users = await DB().select_users_by_role_and_sub_info(session,
                                                                 role=role,
                                                                 sub_info=sub_info)

        # рассылаем изменения по юзерам
        for user_data in users:
            try:
                # создаем расписание с изменениями
                path = await PARSER.parse(str(role), str(sub_info), str(weekday), user_id=user_data.id)
                schedule = FSInputFile(path)
                await send_schedule(chat_id=user_data.id,
                                    short_name_text_mes='changed_schedule',
                                    role=role,
                                    sub_info=sub_info,
                                    weekday=int(weekday),
                                    lang=user_data.lang,
                                    schedule=schedule,
                                    disable_notifications=False)
                await asyncio.sleep(0.5)
            except TelegramForbiddenError:  # возникает когда пользователь заблокировал бота
                pass
                # TODO: как то удалять пользователей из базы, если оно заблокал бота
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                logging.error(f'|changes| {e} \n{str(user_data.id) + " " + role + " " + sub_info}')
