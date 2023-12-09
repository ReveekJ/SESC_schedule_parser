import asyncio
from aiogram import Bot, Dispatcher
from handlers import registration, mainPage
from config import TOKEN


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(registration.router, mainPage.router)
    print('Старт')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
