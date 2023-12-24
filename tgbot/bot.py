import asyncio
from aiogram import Dispatcher
from handlers import registration, mainPage, allSchedule, auxiliary
from tgbot.handlers.auxiliary import bot


async def main():
    dp = Dispatcher()
    dp.include_routers(auxiliary.router, registration.router, allSchedule.router, mainPage.router)

    print('запуск')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
