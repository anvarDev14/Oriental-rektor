from aiogram import executor

from loader import dp
import middlewares
import filters
import handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.database import Database


async def on_startup(dispatcher):
    # Databaseni yaratish
    db = Database()
    db.create_table_users()
    db.create_table_channels()

    # Middlewares va filtersni sozlash
    middlewares.setup(dispatcher)
    filters.setup(dispatcher)

    # Birlamchi komandalar (/start va /help)
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)