import asyncio
import datetime

from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.tgbot import feedback, auxiliary, admin
from src.tgbot.auxiliary import bot
from src.tgbot.changes.changes import sending_schedule_changes
from src.tgbot.elective_course import dialogs
from src.tgbot.for_administration import administration_work
from src.tgbot.main_work import allSchedule, relogin, mainPage, registration, optional_menu
from src.tgbot.settings import dialogs as settings
from src.tgbot.settings.dialogs import dialog

from src.utils.nats_connect import connect_to_nats
from src.utils.delayed_remove_elective_changes.start_delayed_consumer import start_delayed_consumer
from src.utils.delayed_remove_elective_changes.create_stream import create_delayed_elective_changes_stream

from src.config import (NATS_SERVER, NATS_DELAYED_CONSUMER_STREAM, NATS_DELAYED_CONSUMER_SUBJECT,
                        NATS_DELAYED_CONSUMER_DURABLE_NAME, PATH_TO_PROJECT)
import sys
sys.path.append(f'{PATH_TO_PROJECT}/proto')


def set_tasks(scheduler: AsyncIOScheduler):
    times = [datetime.time(2, 0, 0),
             datetime.time(5, 0, 0),
             datetime.time(6, 0, 0),
             datetime.time(7, 0, 0),
             datetime.time(9, 30, 0),
             datetime.time(10, 20, 0),
             datetime.time(11, 10, 0),
             datetime.time(12, 10, 0),
             datetime.time(13, 5, 0),
             datetime.time(14, 5, 0),
             datetime.time(15, 5, 0),
             datetime.time(18, 0, 0),
             datetime.time(20, 0, 0)]

    for i in times[:len(times) - 1]:
        # минус 2, так как сервер находится в Москве
        scheduler.add_job(sending_schedule_changes, CronTrigger(hour=i.hour - 2, minute=i.minute, second=i.second))

    scheduler.add_job(sending_schedule_changes, CronTrigger(hour=times[-1].hour, minute=times[-1].minute,
                                                            second=times[-1].second),
                      next_run_time=datetime.datetime.now())


async def main():
    # ставим выполняться проверку изменений
    dp = Dispatcher()

    scheduler = AsyncIOScheduler()
    set_tasks(scheduler)
    scheduler.start()

    nc, js = await connect_to_nats(servers=NATS_SERVER)

    dp.include_routers(administration_work.router, auxiliary.router, registration.router, allSchedule.router,
                       optional_menu.router, mainPage.router, relogin.router, admin.router, feedback.router,
                       dialogs.admin_work, dialogs.auth_dialog, dialogs.user_dialog, settings.dialog, settings.router)
    setup_dialogs(dp)

    try:
        await create_delayed_elective_changes_stream(js)
        await asyncio.gather(
            dp.start_polling(
                bot,
                js=js
            ),
            start_delayed_consumer(
                nc=nc,
                js=js,
                subject=NATS_DELAYED_CONSUMER_SUBJECT,
                stream=NATS_DELAYED_CONSUMER_STREAM,
                durable_name=NATS_DELAYED_CONSUMER_DURABLE_NAME
            )
        )
    except Exception as e:
        print(e)
    finally:
        await nc.close()


if __name__ == '__main__':
    asyncio.run(main())
