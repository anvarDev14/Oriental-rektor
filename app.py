"""
Asosiy bot fayli
python app.py bilan ishga tushiring
"""
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMINS, RECTOR_ID, is_admin, is_rector
from handlers import register_all_attendance_handlers, handle_attendance_deeplink
from utils import AttendanceDB
from keyboards import user_main_menu


# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ==================== STATES ====================

class BroadcastState(StatesGroup):
    content = State()
    confirm = State()


class ChannelState(StatesGroup):
    add_channel = State()


class FeedbackState(StatesGroup):
    writing = State()
    confirm = State()


class ReplyFeedbackState(StatesGroup):
    selecting = State()
    replying = State()


# ==================== KEYBOARDS ====================

def admin_menu():
    """Admin uchun reply keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📋 Davomat"),
        KeyboardButton("📊 Statistika")
    )
    keyboard.add(
        KeyboardButton("📢 Reklama yuborish"),
        KeyboardButton("📺 Kanallar")
    )
    keyboard.add(
        KeyboardButton("👥 Foydalanuvchilar"),
        KeyboardButton("⚙️ Sozlamalar")
    )
    return keyboard


def rector_menu():
    """Rektor uchun reply keyboard"""
    db = AttendanceDB()
    pending = db.count_pending_feedbacks()

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📋 Davomat"),
        KeyboardButton("📊 Statistika")
    )
    keyboard.add(
        KeyboardButton(f"📬 Xabarlar ({pending})"),
        KeyboardButton("📢 Reklama yuborish")
    )
    keyboard.add(
        KeyboardButton("📺 Kanallar"),
        KeyboardButton("⚙️ Sozlamalar")
    )
    return keyboard


def cancel_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Bekor qilish"))
    return keyboard


def feedback_confirm_kb():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="feedback_confirm"),
        InlineKeyboardButton("✏️ Tahrirlash", callback_data="feedback_edit")
    )
    keyboard.add(
        InlineKeyboardButton("❌ Bekor qilish", callback_data="feedback_cancel")
    )
    return keyboard


def confirm_kb():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="broadcast_confirm"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="broadcast_cancel")
    )
    return keyboard


# ==================== START HANDLER ====================

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    """Start komandasi"""
    await state.finish()
    args = message.get_args()

    # QR kod orqali kelgan bo'lsa
    if args and args.startswith("att_"):
        await handle_attendance_deeplink(message)
        return

    db = AttendanceDB()
    is_registered = db.is_student_registered(message.from_user.id)

    # Rektor
    if is_rector(message.from_user.id):
        await message.answer(
            f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            f"🎓 Siz rektor sifatida kirdingiz.",
            reply_markup=rector_menu()
        )
    # Admin
    elif is_admin(message.from_user.id):
        await message.answer(
            f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            f"👨‍💼 Siz admin sifatida kirdingiz.",
            reply_markup=admin_menu()
        )
    # Oddiy user
    else:
        await message.answer(
            f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            f"📋 Davomat qilish uchun avval ro'yxatdan o'ting.\n"
            f"📱 Keyin darsda QR kodni skanerlang.",
            reply_markup=user_main_menu(is_registered=is_registered)
        )


# ==================== 📝 XABAR YOZISH (USER -> REKTOR) ====================

@dp.message_handler(text="📝 Xabar yozish")
async def start_feedback(message: types.Message):
    await message.answer(
        "📝 <b>Xabar yozish</b>\n\n"
        "O'z fikr, taklif, shikoyat yoki savolingizni yozing.\n\n"
        "📌 Xabaringiz to'g'ridan-to'g'ri rektorga yuboriladi.\n\n"
        "Matn, rasm, video yoki fayl yuborishingiz mumkin.",
        reply_markup=cancel_kb()
    )
    await FeedbackState.writing.set()


@dp.message_handler(state=FeedbackState.writing, content_types=types.ContentType.ANY)
async def process_feedback(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        db = AttendanceDB()
        is_registered = db.is_student_registered(message.from_user.id)
        await message.answer("❌ Bekor qilindi.", reply_markup=user_main_menu(is_registered))
        return

    # Xabar ma'lumotlarini saqlash
    file_id = None
    message_type = "text"
    text = message.text or message.caption or ""

    if message.photo:
        file_id = message.photo[-1].file_id
        message_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        message_type = "video"
    elif message.document:
        file_id = message.document.file_id
        message_type = "document"
    elif message.voice:
        file_id = message.voice.file_id
        message_type = "voice"

    await state.update_data(
        message_type=message_type,
        message_text=text,
        file_id=file_id,
        original_message_id=message.message_id
    )

    # Preview ko'rsatish
    preview_text = text[:200] + "..." if len(text) > 200 else text

    await message.answer(
        f"📋 <b>Xabaringiz:</b>\n\n"
        f"{preview_text}\n\n"
        f"📎 Turi: {message_type}\n\n"
        "Tasdiqlaysizmi?",
        reply_markup=feedback_confirm_kb()
    )
    await FeedbackState.confirm.set()


@dp.callback_query_handler(text="feedback_cancel", state=FeedbackState.confirm)
async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    db = AttendanceDB()
    is_registered = db.is_student_registered(callback.from_user.id)

    await callback.message.edit_text("❌ Xabar bekor qilindi.")
    await callback.message.answer("Bosh menyu:", reply_markup=user_main_menu(is_registered))


@dp.callback_query_handler(text="feedback_edit", state=FeedbackState.confirm)
async def edit_feedback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Xabarni qayta yozing:</b>\n\n"
        "Yangi xabaringizni yuboring."
    )
    await callback.message.answer("Xabaringizni yozing:", reply_markup=cancel_kb())
    await FeedbackState.writing.set()


@dp.callback_query_handler(text="feedback_confirm", state=FeedbackState.confirm)
async def confirm_feedback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()

    db = AttendanceDB()
    user = callback.from_user

    # Bazaga saqlash
    msg_id = db.save_feedback(
        user_id=user.id,
        user_name=user.full_name,
        user_username=user.username,
        message_type=data['message_type'],
        message_text=data['message_text'],
        file_id=data.get('file_id')
    )

    # Rektorga yuborish
    if RECTOR_ID:
        try:
            # Xabar matni
            rector_text = (
                f"📬 <b>Yangi xabar #{msg_id}</b>\n\n"
                f"👤 Kimdan: {user.full_name}\n"
                f"🆔 Username: @{user.username or 'yo`q'}\n"
                f"📅 Vaqt: {callback.message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"💬 <b>Xabar:</b>\n{data['message_text'] or '[Media fayl]'}"
            )

            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("💬 Javob berish", callback_data=f"reply_feedback:{msg_id}")
            )

            # Media bilan yuborish
            if data['message_type'] == 'photo' and data.get('file_id'):
                await bot.send_photo(
                    RECTOR_ID,
                    photo=data['file_id'],
                    caption=rector_text,
                    reply_markup=keyboard
                )
            elif data['message_type'] == 'video' and data.get('file_id'):
                await bot.send_video(
                    RECTOR_ID,
                    video=data['file_id'],
                    caption=rector_text,
                    reply_markup=keyboard
                )
            elif data['message_type'] == 'document' and data.get('file_id'):
                await bot.send_document(
                    RECTOR_ID,
                    document=data['file_id'],
                    caption=rector_text,
                    reply_markup=keyboard
                )
            elif data['message_type'] == 'voice' and data.get('file_id'):
                await bot.send_voice(
                    RECTOR_ID,
                    voice=data['file_id'],
                    caption=rector_text,
                    reply_markup=keyboard
                )
            else:
                await bot.send_message(
                    RECTOR_ID,
                    rector_text,
                    reply_markup=keyboard
                )
        except Exception as e:
            print(f"Rektorga yuborishda xato: {e}")

    # Userga tasdiqlash
    is_registered = db.is_student_registered(callback.from_user.id)

    await callback.message.edit_text(
        f"✅ <b>Xabaringiz yuborildi!</b>\n\n"
        f"📬 Xabar raqami: #{msg_id}\n\n"
        f"Javob kelganda sizga xabar beramiz."
    )
    await callback.message.answer("Bosh menyu:", reply_markup=user_main_menu(is_registered))


# ==================== 📬 REKTOR XABARLAR BO'LIMI ====================

@dp.message_handler(lambda m: is_rector(m.from_user.id), text_contains="📬 Xabarlar")
async def show_rector_messages(message: types.Message):
    db = AttendanceDB()
    feedbacks = db.get_pending_feedbacks()

    if not feedbacks:
        await message.answer(
            "📬 <b>Xabarlar</b>\n\n"
            "✅ Barcha xabarlarga javob berilgan!",
            reply_markup=rector_menu()
        )
        return

    keyboard = InlineKeyboardMarkup(row_width=1)

    text = f"📬 <b>Javob kutayotgan xabarlar ({len(feedbacks)} ta)</b>\n\n"

    for fb in feedbacks[:10]:
        short_text = fb['message_text'][:30] + "..." if fb['message_text'] and len(fb['message_text']) > 30 else fb['message_text'] or "[Media]"
        text += f"#{fb['id']} - {fb['user_name']}: {short_text}\n"

        keyboard.add(
            InlineKeyboardButton(
                f"#{fb['id']} - {fb['user_name'][:20]}",
                callback_data=f"view_feedback:{fb['id']}"
            )
        )

    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_rector"))

    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith("view_feedback:"))
async def view_feedback_detail(callback: types.CallbackQuery):
    msg_id = int(callback.data.split(":")[1])

    db = AttendanceDB()
    fb = db.get_feedback_by_id(msg_id)

    if not fb:
        await callback.answer("Xabar topilmadi!", show_alert=True)
        return

    text = (
        f"📬 <b>Xabar #{fb['id']}</b>\n\n"
        f"👤 Kimdan: {fb['user_name']}\n"
        f"🆔 Username: @{fb['user_username'] or 'yo`q'}\n"
        f"📅 Yuborilgan: {fb['created_at']}\n"
        f"📎 Turi: {fb['message_type']}\n\n"
        f"💬 <b>Xabar:</b>\n{fb['message_text'] or '[Media fayl]'}"
    )

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💬 Javob berish", callback_data=f"reply_feedback:{msg_id}")
    )
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_feedbacks"))

    # Media bilan ko'rsatish
    if fb['message_type'] == 'photo' and fb.get('file_id'):
        await callback.message.delete()
        await callback.message.answer_photo(
            fb['file_id'],
            caption=text,
            reply_markup=keyboard
        )
    elif fb['message_type'] == 'video' and fb.get('file_id'):
        await callback.message.delete()
        await callback.message.answer_video(
            fb['file_id'],
            caption=text,
            reply_markup=keyboard
        )
    elif fb['message_type'] == 'document' and fb.get('file_id'):
        await callback.message.delete()
        await callback.message.answer_document(
            fb['file_id'],
            caption=text,
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("reply_feedback:"))
async def start_reply_feedback(callback: types.CallbackQuery, state: FSMContext):
    msg_id = int(callback.data.split(":")[1])

    await state.update_data(feedback_id=msg_id)

    await callback.message.answer(
        "💬 <b>Javob yozish</b>\n\n"
        "Javobingizni yozing:",
        reply_markup=cancel_kb()
    )
    await ReplyFeedbackState.replying.set()
    await callback.answer()


@dp.message_handler(state=ReplyFeedbackState.replying)
async def process_reply_feedback(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=rector_menu())
        return

    data = await state.get_data()
    msg_id = data['feedback_id']
    reply_text = message.text

    db = AttendanceDB()
    fb = db.get_feedback_by_id(msg_id)

    if not fb:
        await state.finish()
        await message.answer("❌ Xabar topilmadi!", reply_markup=rector_menu())
        return

    # Bazaga javobni saqlash
    db.reply_feedback(msg_id, reply_text)

    # Userga javob yuborish
    try:
        await bot.send_message(
            fb['user_id'],
            f"📬 <b>Xabaringizga javob keldi!</b>\n\n"
            f"📝 Sizning xabaringiz:\n<i>{fb['message_text'][:100] or '[Media fayl]'}...</i>\n\n"
            f"💬 <b>Rektor javobi:</b>\n{reply_text}"
        )
    except Exception as e:
        print(f"Userga javob yuborishda xato: {e}")

    await state.finish()

    await message.answer(
        f"✅ <b>Javob yuborildi!</b>\n\n"
        f"Xabar #{msg_id} ga javob berildi.",
        reply_markup=rector_menu()
    )


@dp.callback_query_handler(text="back_to_feedbacks")
async def back_to_feedbacks(callback: types.CallbackQuery):
    db = AttendanceDB()
    feedbacks = db.get_pending_feedbacks()

    if not feedbacks:
        await callback.message.edit_text(
            "📬 <b>Xabarlar</b>\n\n"
            "✅ Barcha xabarlarga javob berilgan!"
        )
        return

    keyboard = InlineKeyboardMarkup(row_width=1)

    text = f"📬 <b>Javob kutayotgan xabarlar ({len(feedbacks)} ta)</b>\n\n"

    for fb in feedbacks[:10]:
        short_text = fb['message_text'][:30] + "..." if fb['message_text'] and len(fb['message_text']) > 30 else fb['message_text'] or "[Media]"
        text += f"#{fb['id']} - {fb['user_name']}: {short_text}\n"

        keyboard.add(
            InlineKeyboardButton(
                f"#{fb['id']} - {fb['user_name'][:20]}",
                callback_data=f"view_feedback:{fb['id']}"
            )
        )

    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_rector"))

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard)

    await callback.answer()


@dp.callback_query_handler(text="back_rector")
async def back_to_rector_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Bosh menyu:", reply_markup=rector_menu())


# ==================== 📊 STATISTIKA ====================

@dp.message_handler(lambda m: is_admin(m.from_user.id) or is_rector(m.from_user.id), text="📊 Statistika")
async def admin_statistics(message: types.Message):
    db = AttendanceDB()
    stats = db.get_attendance_stats()

    directions = db.get_all_directions()
    dir_text = ""
    for d in directions:
        groups = db.get_groups_by_direction(d)
        dir_text += f"📚 {d}: {len(groups)} ta guruh\n"

    await message.answer(
        f"📈 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami talabalar: <b>{stats['total_students']}</b>\n"
        f"📚 Jami darslar: <b>{stats['total_sessions']}</b>\n"
        f"✅ Jami davomat: <b>{stats['total_present']}</b>\n\n"
        f"<b>Yo'nalishlar:</b>\n{dir_text}"
    )


# ==================== 📢 REKLAMA YUBORISH ====================

@dp.message_handler(lambda m: is_admin(m.from_user.id) or is_rector(m.from_user.id), text="📢 Reklama yuborish")
async def start_broadcast(message: types.Message):
    await message.answer(
        "📢 <b>Reklama yuborish</b>\n\n"
        "Reklama kontentini yuboring:\n"
        "- Matn\n"
        "- Rasm\n"
        "- Video\n"
        "- Fayl\n\n"
        "Yoki bekor qilish uchun tugmani bosing.",
        reply_markup=cancel_kb()
    )
    await BroadcastState.content.set()


@dp.message_handler(state=BroadcastState.content, content_types=types.ContentType.ANY)
async def process_broadcast_content(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        if is_rector(message.from_user.id):
            await message.answer("❌ Bekor qilindi.", reply_markup=rector_menu())
        else:
            await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    await state.update_data(
        content_type=message.content_type,
        message_id=message.message_id,
        chat_id=message.chat.id
    )

    await message.answer(
        "👆 <b>Reklama preview</b>\n\n"
        "Shu kontentni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?",
        reply_markup=confirm_kb()
    )
    await BroadcastState.confirm.set()


@dp.callback_query_handler(text="broadcast_cancel", state=BroadcastState.confirm)
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("❌ Reklama bekor qilindi.")

    if is_rector(callback.from_user.id):
        await callback.message.answer("Bosh menyu:", reply_markup=rector_menu())
    else:
        await callback.message.answer("Bosh menyu:", reply_markup=admin_menu())


@dp.callback_query_handler(text="broadcast_confirm", state=BroadcastState.confirm)
async def confirm_broadcast(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()

    await callback.message.edit_text("📤 Reklama yuborilmoqda...")

    db = AttendanceDB()

    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM students")
    users = cursor.fetchall()
    conn.close()

    success = 0
    failed = 0

    for user in users:
        try:
            await bot.copy_message(
                chat_id=user[0],
                from_chat_id=data['chat_id'],
                message_id=data['message_id']
            )
            success += 1
        except Exception as e:
            failed += 1

    if is_rector(callback.from_user.id):
        kb = rector_menu()
    else:
        kb = admin_menu()

    await callback.message.answer(
        f"✅ <b>Reklama yuborildi!</b>\n\n"
        f"📤 Yuborildi: {success}\n"
        f"❌ Yuborilmadi: {failed}",
        reply_markup=kb
    )


# ==================== 📺 KANALLAR ====================

import json
import os

CHANNELS_FILE = "data/channels.json"

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_channels(channels):
    os.makedirs("data", exist_ok=True)
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f)


@dp.message_handler(lambda m: is_admin(m.from_user.id) or is_rector(m.from_user.id), text="📺 Kanallar")
async def show_channels(message: types.Message):
    channels = load_channels()

    keyboard = InlineKeyboardMarkup(row_width=1)

    if channels:
        text = "📺 <b>Majburiy obuna kanallari:</b>\n\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch}\n"
            keyboard.add(
                InlineKeyboardButton(f"❌ {ch} ni o'chirish", callback_data=f"del_channel:{ch}")
            )
    else:
        text = "📺 <b>Majburiy obuna kanallari:</b>\n\nHozircha kanallar yo'q."

    keyboard.add(InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin"))

    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(text="add_channel")
async def add_channel_start(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📺 <b>Kanal qo'shish</b>\n\n"
        "Kanal username ni kiriting:\n"
        "<i>(Masalan: @kanal_nomi)</i>"
    )
    await callback.message.answer("Kanal username:", reply_markup=cancel_kb())
    await ChannelState.add_channel.set()


@dp.message_handler(state=ChannelState.add_channel)
async def add_channel_process(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        if is_rector(message.from_user.id):
            await message.answer("❌ Bekor qilindi.", reply_markup=rector_menu())
        else:
            await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu())
        return

    channel = message.text.strip()
    if not channel.startswith("@"):
        channel = "@" + channel

    channels = load_channels()

    if channel in channels:
        kb = rector_menu() if is_rector(message.from_user.id) else admin_menu()
        await message.answer("⚠️ Bu kanal allaqachon qo'shilgan!", reply_markup=kb)
    else:
        channels.append(channel)
        save_channels(channels)
        kb = rector_menu() if is_rector(message.from_user.id) else admin_menu()
        await message.answer(f"✅ Kanal qo'shildi: {channel}", reply_markup=kb)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("del_channel:"))
async def delete_channel(callback: types.CallbackQuery):
    channel = callback.data.split(":")[1]

    channels = load_channels()
    if channel in channels:
        channels.remove(channel)
        save_channels(channels)
        await callback.answer(f"✅ {channel} o'chirildi!")

    keyboard = InlineKeyboardMarkup(row_width=1)

    if channels:
        text = "📺 <b>Majburiy obuna kanallari:</b>\n\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch}\n"
            keyboard.add(
                InlineKeyboardButton(f"❌ {ch} ni o'chirish", callback_data=f"del_channel:{ch}")
            )
    else:
        text = "📺 <b>Majburiy obuna kanallari:</b>\n\nHozircha kanallar yo'q."

    keyboard.add(InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin"))

    await callback.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(text="back_admin")
async def back_to_admin(callback: types.CallbackQuery):
    await callback.message.delete()
    if is_rector(callback.from_user.id):
        await callback.message.answer("Bosh menyu:", reply_markup=rector_menu())
    else:
        await callback.message.answer("Bosh menyu:", reply_markup=admin_menu())


# ==================== 👥 FOYDALANUVCHILAR ====================

@dp.message_handler(lambda m: is_admin(m.from_user.id), text="👥 Foydalanuvchilar")
async def admin_users(message: types.Message):
    db = AttendanceDB()

    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT direction, COUNT(*) FROM students 
        GROUP BY direction ORDER BY COUNT(*) DESC
    """)
    by_direction = cursor.fetchall()

    cursor.execute("""
        SELECT direction, group_name, COUNT(*) FROM students 
        GROUP BY direction, group_name ORDER BY direction, group_name
    """)
    by_group = cursor.fetchall()

    conn.close()

    text = "👥 <b>Foydalanuvchilar</b>\n\n"
    text += "<b>Yo'nalishlar bo'yicha:</b>\n"
    for d, count in by_direction:
        text += f"📚 {d}: {count} ta\n"

    text += "\n<b>Guruhlar bo'yicha:</b>\n"
    for d, g, count in by_group[:15]:
        text += f"👥 {d} - {g}: {count} ta\n"

    if len(by_group) > 15:
        text += f"\n... va yana {len(by_group) - 15} ta guruh"

    await message.answer(text)


# ==================== ⚙️ SOZLAMALAR ====================

@dp.message_handler(lambda m: is_admin(m.from_user.id) or is_rector(m.from_user.id), text="⚙️ Sozlamalar")
async def admin_settings(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📚 Yo'nalish qo'shish", callback_data="add_direction"),
        InlineKeyboardButton("👥 Guruh qo'shish", callback_data="add_group"),
        InlineKeyboardButton("🗑 Ma'lumotlarni tozalash", callback_data="clear_data")
    )

    await message.answer(
        "⚙️ <b>Sozlamalar</b>\n\n"
        "Quyidagi amallardan birini tanlang:",
        reply_markup=keyboard
    )


@dp.callback_query_handler(text="clear_data")
async def clear_data_confirm(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Ha, tozalash", callback_data="clear_confirm"),
        InlineKeyboardButton("❌ Yo'q", callback_data="back_admin")
    )

    await callback.message.edit_text(
        "⚠️ <b>Diqqat!</b>\n\n"
        "Barcha davomat yozuvlari o'chiriladi!\n"
        "Davom etasizmi?",
        reply_markup=keyboard
    )


@dp.callback_query_handler(text="clear_confirm")
async def clear_data_execute(callback: types.CallbackQuery):
    db = AttendanceDB()

    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance_records")
    cursor.execute("DELETE FROM attendance_sessions")
    conn.commit()
    conn.close()

    await callback.message.edit_text("✅ Davomat yozuvlari tozalandi!")

    if is_rector(callback.from_user.id):
        await callback.message.answer("Bosh menyu:", reply_markup=rector_menu())
    else:
        await callback.message.answer("Bosh menyu:", reply_markup=admin_menu())


# ==================== USER HANDLERS ====================

@dp.message_handler(text="ℹ️ Yordam")
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 <b>Yordam</b>\n\n"
        "1️⃣ <b>Ro'yxatdan o'tish</b> - Ism, ID, yo'nalish, guruh kiriting\n\n"
        "2️⃣ <b>Davomat qilish</b> - Darsda QR kodni telefon kamerasi bilan skanerlang\n\n"
        "3️⃣ <b>Davomatni ko'rish</b> - 📊 Mening davomatim tugmasini bosing\n\n"
        "4️⃣ <b>Xabar yozish</b> - Rektorga to'g'ridan-to'g'ri xabar yuborish\n\n"
        "❓ Savollar bo'lsa admin bilan bog'laning."
    )


# ==================== SESSION TUGMALARI ====================

@dp.callback_query_handler(lambda c: c.data.startswith("session_att:"))
async def show_session_attendance(callback: types.CallbackQuery):
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    session = db.get_session_by_id(session_id)
    attendance = db.get_session_attendance(session_id)

    if not session:
        await callback.answer("Sessiya topilmadi!", show_alert=True)
        return

    if attendance:
        text = f"📊 <b>Davomat: {session['subject']}</b>\n"
        text += f"👥 Guruh: {session['group_name']}\n"
        text += f"📅 Sana: {session['session_date']}\n\n"
        text += f"<b>Kelganlar ({len(attendance)} ta):</b>\n\n"

        for i, a in enumerate(attendance, 1):
            text += f"{i}. ✅ {a['full_name']}\n"
    else:
        text = f"📊 <b>Davomat: {session['subject']}</b>\n\n"
        text += "❌ Hali hech kim davomat qilmagan."

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Yangilash", callback_data=f"session_att:{session_id}"),
        InlineKeyboardButton("📥 Excel", callback_data=f"export_session:{session_id}")
    )
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"view_session:{session_id}"))

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("export_session:"))
async def export_session_excel(callback: types.CallbackQuery):
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    session = db.get_session_by_id(session_id)

    if not session:
        await callback.answer("Sessiya topilmadi!", show_alert=True)
        return

    report_data = db.get_weekly_report(session['direction'], session['group_name'])

    if not report_data['students']:
        await callback.answer("Talabalar yo'q!", show_alert=True)
        return

    from utils.excel_export import create_attendance_report
    from datetime import datetime

    excel_file = create_attendance_report(report_data)

    await callback.message.answer_document(
        types.InputFile(
            excel_file,
            filename=f"davomat_{session['group_name']}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        ),
        caption=(
            f"📊 <b>Davomat hisoboti</b>\n\n"
            f"📚 Fan: {session['subject']}\n"
            f"👥 Guruh: {session['group_name']}\n"
            f"📅 Sana: {session['session_date']}"
        )
    )
    await callback.answer("✅ Excel tayyor!")


@dp.callback_query_handler(text="back_to_sessions")
async def back_to_sessions(callback: types.CallbackQuery):
    db = AttendanceDB()
    sessions = db.get_active_sessions()

    if not sessions:
        await callback.message.edit_text(
            "📋 <b>Faol darslar</b>\n\nHozirda faol darslar yo'q.",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_attendance")
            )
        )
        return

    keyboard = InlineKeyboardMarkup(row_width=1)

    for session in sessions[:10]:
        keyboard.add(
            InlineKeyboardButton(
                f"📚 {session['subject']} | {session['group_name']} | {session['session_date']}",
                callback_data=f"view_session:{session['session_id']}"
            )
        )

    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_attendance"))

    await callback.message.edit_text(
        f"📋 <b>Faol darslar ({len(sessions)} ta)</b>\n\nKo'rish uchun tanlang:",
        reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query_handler(text="back_to_attendance")
async def back_to_attendance_menu(callback: types.CallbackQuery):
    from keyboards.attendance_kb import attendance_admin_menu

    await callback.message.edit_text(
        "📋 <b>Davomat boshqaruvi</b>\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=attendance_admin_menu()
    )
    await callback.answer()


# ==================== DAVOMAT HANDLERLARINI QO'SHISH ====================

register_all_attendance_handlers(dp)


# ==================== BOTNI ISHGA TUSHIRISH ====================

if __name__ == '__main__':
    print("🤖 Bot ishga tushmoqda...")
    print(f"👥 Adminlar: {ADMINS}")
    print(f"🎓 Rektor ID: {RECTOR_ID}")
    executor.start_polling(dp, skip_updates=True)
