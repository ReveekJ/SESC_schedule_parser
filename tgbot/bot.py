import asyncio
from aiogram import Bot, Dispatcher
from handlers import registration, mainPage, allSchedule
from config import TOKEN
from tgbot.parser import PARSER


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(registration.router, allSchedule.router, mainPage.router)

    # set up parser
    PARSER.parse('group', '1', '1')

    print('запуск')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
