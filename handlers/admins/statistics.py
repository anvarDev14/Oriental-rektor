from aiogram import types

from loader import dp
from filters.is_admin import IsAdmin
from utils.db_api.database import Database


@dp.message_handler(IsAdmin(), text="📊 Statistika")
async def show_statistics(message: types.Message):
    db = Database()
    
    total_users = db.count_users()
    channels_count = len(db.get_all_channels())
    
    text = (
        f"📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar soni: <b>{total_users}</b>\n"
        f"📺 Majburiy kanallar: <b>{channels_count}</b>\n"
    )
    
    await message.answer(text)
