from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from filters.is_admin import IsAdmin
from states.message_states import ChannelStates
from keyboards.inline.admin_keyboard import channel_actions_keyboard, delete_channel_keyboard
from keyboards.default.menu import cancel_menu, admin_menu
from utils.db_api.database import Database


import os

# Faylning boshida, import qatorlaridan keyin:
def get_db():
    data_dir = "/app/data"
    db_path = os.path.join(data_dir, "database.db")
    return Database(path_to_db=db_path)

# Keyin barcha `db = Database()` o'rniga:
# db = get_db()




@dp.message_handler(IsAdmin(), text="📺 Kanallar")
async def channels_menu(message: types.Message):
    db = Database()
    channels = db.get_all_channels()

    text = "📺 <b>Majburiy obuna kanallari</b>\n\n"

    if channels:
        text += "Ro'yxatdagi kanallar:\n"
        for i, channel in enumerate(channels, 1):
            text += f"{i}. {channel[2]} - <code>{channel[1]}</code>\n"
    else:
        text += "Hozircha kanallar qo'shilmagan."

    await message.answer(text, reply_markup=channel_actions_keyboard())


@dp.callback_query_handler(text="back_to_channels")
async def back_to_channels(call: types.CallbackQuery):
    db = Database()
    channels = db.get_all_channels()

    text = "📺 <b>Majburiy obuna kanallari</b>\n\n"

    if channels:
        text += "Ro'yxatdagi kanallar:\n"
        for i, channel in enumerate(channels, 1):
            text += f"{i}. {channel[2]} - <code>{channel[1]}</code>\n"
    else:
        text += "Hozircha kanallar qo'shilmagan."

    await call.message.edit_text(text, reply_markup=channel_actions_keyboard())
    await call.answer()


@dp.callback_query_handler(text="add_channel")
async def add_channel_start(call: types.CallbackQuery, state: FSMContext):
    # ❌ XATO: call.message.edit_text() bilan cancel_menu() ishlamaydi
    # ✅ TUZATISH: Avval delete, keyin answer

    await call.message.delete()  # Eski xabarni o'chirish
    await call.message.answer(  # Yangi xabar yuborish
        "➕ <b>Yangi kanal qo'shish</b>\n\n"
        "Kanal ID sini yuboring.\n\n"
        "❗️ Kanal ID'sini olish uchun:\n"
        "1. Botni kanalga admin qiling\n"
        "2. @username yoki -100xxxxxxxx formatida ID yuboring\n\n"
        "Masalan: <code>@myChannel</code> yoki <code>-1001234567890</code>",
        reply_markup=cancel_menu()
    )
    await ChannelStates.waiting_for_channel_id.set()
    await call.answer()


@dp.message_handler(IsAdmin(), state=ChannelStates.waiting_for_channel_id)
async def receive_channel_id(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("❌ Kanal qo'shish bekor qilindi.", reply_markup=admin_menu())
        await state.finish()
        return

    channel_id = message.text.strip()

    try:
        chat = await bot.get_chat(channel_id)

        async with state.proxy() as data:
            data['channel_id'] = str(chat.id)
            data['channel_title'] = chat.title

        await message.answer(
            f"✅ Kanal topildi: <b>{chat.title}</b>\n\n"
            f"Endi kanal uchun URL manzilini yuboring.\n"
            f"Masalan: <code>https://t.me/myChannel</code>",
            reply_markup=cancel_menu()
        )
        await ChannelStates.waiting_for_channel_url.set()
    except Exception as e:
        await message.answer(
            f"❌ Xato: Kanal topilmadi yoki bot admin emas!\n\n"
            f"Xato: {e}\n\n"
            f"Qaytadan urinib ko'ring:",
            reply_markup=cancel_menu()
        )


@dp.message_handler(IsAdmin(), state=ChannelStates.waiting_for_channel_url)
async def receive_channel_url(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("❌ Kanal qo'shish bekor qilindi.", reply_markup=admin_menu())
        await state.finish()
        return

    channel_url = message.text.strip()

    if not channel_url.startswith("https://t.me/"):
        await message.answer(
            "❌ Noto'g'ri URL format!\n\n"
            "URL https://t.me/ bilan boshlanishi kerak.\n"
            "Masalan: <code>https://t.me/myChannel</code>",
            reply_markup=cancel_menu()
        )
        return

    data = await state.get_data()
    channel_id = data['channel_id']
    channel_title = data['channel_title']

    db = Database()
    try:
        db.add_channel(channel_id, channel_title, channel_url)
        await message.answer(
            f"✅ Kanal muvaffaqiyatli qo'shildi!\n\n"
            f"📺 Kanal: <b>{channel_title}</b>\n"
            f"🆔 ID: <code>{channel_id}</code>\n"
            f"🔗 URL: {channel_url}",
            reply_markup=admin_menu()
        )
    except Exception as e:
        await message.answer(
            f"❌ Xato: Kanal qo'shishda muammo!\n\n"
            f"Bu kanal allaqachon qo'shilgan bo'lishi mumkin.\n"
            f"Xato: {e}",
            reply_markup=admin_menu()
        )

    await state.finish()


@dp.callback_query_handler(text="delete_channel")
async def delete_channel_start(call: types.CallbackQuery):
    db = Database()
    channels = db.get_all_channels()

    if not channels:
        await call.answer("❌ O'chiradigan kanal yo'q!", show_alert=True)
        return

    await call.message.edit_text(
        "🗑 <b>Kanal o'chirish</b>\n\n"
        "O'chirmoqchi bo'lgan kanalni tanlang:",
        reply_markup=delete_channel_keyboard(channels)
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("del_channel_"))
async def confirm_delete_channel(call: types.CallbackQuery):
    channel_id = call.data.replace("del_channel_", "")

    db = Database()
    channel = db.get_channel_by_id(channel_id)

    if channel:
        db.delete_channel(channel_id)
        await call.answer(f"✅ {channel[2]} kanali o'chirildi!", show_alert=True)

        channels = db.get_all_channels()
        text = "📺 <b>Majburiy obuna kanallari</b>\n\n"

        if channels:
            text += "Ro'yxatdagi kanallar:\n"
            for i, ch in enumerate(channels, 1):
                text += f"{i}. {ch[2]} - <code>{ch[1]}</code>\n"
        else:
            text += "Hozircha kanallar qo'shilmagan."

        await call.message.edit_text(text, reply_markup=channel_actions_keyboard())
    else:
        await call.answer("❌ Kanal topilmadi!", show_alert=True)


@dp.message_handler(IsAdmin(), text="❌ Bekor qilish",
                    state=[ChannelStates.waiting_for_channel_id,
                           ChannelStates.waiting_for_channel_url])
async def cancel_channel_add(message: types.Message, state: FSMContext):
    await message.answer("❌ Amal bekor qilindi.", reply_markup=admin_menu())
    await state.finish()