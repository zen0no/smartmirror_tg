from aiogram.utils import executor

from .bot import dp as dispatcher_to_execute


def start_bot():
    executor.start_polling(dispatcher=dispatcher_to_execute, skip_updates=True)