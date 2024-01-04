import asyncio
from aiogram import Dispatcher
from handlers import registration, mainPage, allSchedule, auxiliary
from tgbot.handlers.auxiliary import bot
from tgbot.handlers.auxiliary import sending_schedule_changes
from threading import Thread


async def main():
    dp = Dispatcher()
    dp.include_routers(auxiliary.router, registration.router, allSchedule.router, mainPage.router)
    Thread(target=sending_schedule_changes).start()
    print('запуск')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
