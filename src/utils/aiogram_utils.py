from aiogram.filters import Filter
from aiogram.types import CallbackQuery


class StartsWithFilter(Filter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, callback_query: CallbackQuery):
        return callback_query.data.startswith(self.prefix)
