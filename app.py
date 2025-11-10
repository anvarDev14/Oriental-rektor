from aiogram import executor

from loader import dp
import middlewares
import filters
import handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.database import Database
import os


async def on_startup(dispatcher):
    # Data papkasini yaratish
    data_dir = "/app/data"
    os.makedirs(data_dir, exist_ok=True)

    # Database yo'li
    db_path = os.path.join(data_dir, "database.db")
    print(f"📊 Database path: {db_path}")

    # Database yaratish
    db = Database(path_to_db=db_path)
    db.create_table_users()
    db.create_table_channels()
    print("✅ Database yaratildi!")

    # Middlewares va filtersni sozlash
    middlewares.setup(dispatcher)
    filters.setup(dispatcher)

    # Birlamchi komandalar
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)
    print("🚀 Bot ishga tushdi!")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)