import asyncio
import logging

from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import FSInputFile

from src.database import get_async_session
from src.tgbot.auxiliary import send_schedule
from src.tgbot.parser import PARSER
from src.tgbot.user_models.db import DB
from src.utils.aiogram_utils import delete_last_message, send_main_page


async def sending_schedule_changes():
    # получаем измения
    changes = await PARSER.check_for_changes()

    for elem in changes:
        role = elem.type
        sub_info = elem.second
        weekday = elem.weekday

        sent_users = []
        # schedule = elem.schedule

        async with await get_async_session() as session:
            users = await DB().select_users_by_role_and_sub_info(session,
                                                                 role=role,
                                                                 sub_info=sub_info)

        # рассылаем изменения по юзерам
        for user_data in users:
            if user_data.id in sent_users:
                continue  # еще раз предохраняемся

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

                await delete_last_message(user_data.id)
                main_msg = await send_main_page(user_data.id)
                await DB().update_last_message_id(user_data.id, main_msg.message_id)

                await asyncio.sleep(0.5)
            except TelegramForbiddenError:  # возникает когда пользователь заблокировал бота
                pass
                # TODO: как то удалять пользователей из базы, если оно заблокал бота
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                logging.error(f'|changes| {e} \n{str(user_data.id) + " " + role + " " + sub_info}')
