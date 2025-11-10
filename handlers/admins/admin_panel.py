from aiogram import types

from loader import dp
from filters.is_admin import IsAdmin
from keyboards.default.menu import admin_menu


@dp.message_handler(IsAdmin(), text="/admin")
async def admin_panel(message: types.Message):
    await message.answer(
        "👨‍💼 <b>Admin Panel</b>\n\n"
        "Quyidagi funksiyalardan foydalaning:",
        reply_markup=admin_menu()
    )


@dp.callback_query_handler(text="back_to_admin")
async def back_to_admin(call: types.CallbackQuery):
    await call.message.edit_text(
        "👨‍💼 <b>Admin Panel</b>\n\n"
        "Quyidagi funksiyalardan foydalaning:"
    )
    await call.answer()
