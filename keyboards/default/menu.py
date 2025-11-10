from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def user_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✍️ Xabar yozish"))
    return markup


def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📊 Statistika"),
        KeyboardButton("📢 Reklama yuborish")
    )
    markup.add(KeyboardButton("📺 Kanallar"))
    return markup


def confirm_message_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("✅ Tasdiqlash"),
        KeyboardButton("✏️ Yangilash")
    )
    markup.add(KeyboardButton("❌ Bekor qilish"))
    return markup


def cancel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    return markup
