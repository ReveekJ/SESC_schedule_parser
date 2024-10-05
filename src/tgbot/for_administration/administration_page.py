from aiogram.types import Message, CallbackQuery

from src.tgbot.auxiliary import bot
from src.tgbot.keyboard import admin_functions
from src.tgbot.text import TEXT


async def administration_page(message: Message | CallbackQuery):
    lang = message.from_user.language_code
    user_id = message.chat.id if isinstance(message, Message) else message.message.chat.id

    await bot.send_message(chat_id=user_id,
                           text=TEXT('admin_panel', lang=lang),
                           reply_markup=admin_functions(lang),
                           disable_notification=True)

    if isinstance(message, CallbackQuery):
        await message.answer()
