from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.db_api.database import Database
from keyboards.default.menu import user_menu, admin_menu
from data.config import ADMINS


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    db = Database()

    # Foydalanuvchini bazaga qo'shish
    db.add_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    # Admin yoki oddiy foydalanuvchi tekshirish
    if str(message.from_user.id) in ADMINS:
        await message.answer(
            f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
            f"👨‍💼 Siz <b>admin</b> sifatida kirdingiz.\n\n"
            f"🎛 Admin paneldan foydalaning:",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
            f"📢 Ushbu bot orqali siz o'z fikr va takliflaringizni "
            f"<b>rektor</b> bilan baham ko'rishingiz mumkin.\n\n"
            f"✍️ <b>Xabar yozish</b> tugmasini bosing va taklifingizni yuboring!",
            reply_markup=user_menu()
        )