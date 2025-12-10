"""
Davomat tizimi uchun klaviaturalar
"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from typing import List


# ==================== REPLY KEYBOARDS ====================

def user_main_menu(is_registered: bool = False) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_registered:
        keyboard.add(
            KeyboardButton("📝 Xabar yozish"),
            KeyboardButton("📊 Mening davomatim")
        )
        keyboard.add(
            KeyboardButton("👤 Mening ma'lumotlarim"),
            KeyboardButton("ℹ️ Yordam")
        )
    else:
        keyboard.add(
            KeyboardButton("📝 Xabar yozish"),
            KeyboardButton("📋 Ro'yxatdan o'tish")
        )
        keyboard.add(KeyboardButton("ℹ️ Yordam"))
    
    return keyboard


def admin_attendance_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📊 Statistika"),
        KeyboardButton("📢 Reklama yuborish")
    )
    keyboard.add(
        KeyboardButton("📋 Davomat"),
        KeyboardButton("📺 Kanallar")
    )
    keyboard.add(KeyboardButton("⚙️ Sozlamalar"))
    return keyboard


def phone_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))
    keyboard.add(KeyboardButton("⏭ O'tkazib yuborish"))
    return keyboard


def cancel_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Bekor qilish"))
    return keyboard


def confirm_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("✅ Tasdiqlash"),
        KeyboardButton("❌ Bekor qilish")
    )
    return keyboard


# ==================== INLINE KEYBOARDS ====================

def directions_keyboard(directions: List[str], callback_prefix: str = "dir") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for direction in directions:
        keyboard.add(
            InlineKeyboardButton(
                text=f"📚 {direction}",
                callback_data=f"{callback_prefix}:{direction}"
            )
        )
    
    keyboard.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    return keyboard


def groups_keyboard(groups: List[str], direction: str, 
                   callback_prefix: str = "grp") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=f"👥 {group}",
                callback_data=f"{callback_prefix}:{direction}:{group}"
            )
        )
    
    for i in range(0, len(buttons), 3):
        keyboard.row(*buttons[i:i+3])
    
    keyboard.add(
        InlineKeyboardButton("➕ Yangi guruh", callback_data=f"new_group:{direction}"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_directions")
    )
    
    return keyboard


def attendance_admin_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🆕 Yangi dars", callback_data="new_session"),
        InlineKeyboardButton("📋 Faol darslar", callback_data="active_sessions")
    )
    keyboard.add(
        InlineKeyboardButton("📊 Hisobot olish", callback_data="get_report"),
        InlineKeyboardButton("👥 Talabalar", callback_data="students_list")
    )
    keyboard.add(
        InlineKeyboardButton("➕ Yo'nalish qo'shish", callback_data="add_direction"),
        InlineKeyboardButton("➕ Guruh qo'shish", callback_data="add_group")
    )
    keyboard.add(InlineKeyboardButton("📈 Statistika", callback_data="attendance_stats"))
    
    return keyboard


def session_actions(session_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 QR yangilash", callback_data=f"refresh_qr:{session_id}"),
        InlineKeyboardButton("📊 Davomat", callback_data=f"session_att:{session_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🛑 Yopish", callback_data=f"close_session:{session_id}"),
        InlineKeyboardButton("📥 Excel", callback_data=f"export_session:{session_id}")
    )
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_sessions"))
    
    return keyboard


def duration_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    keyboard.add(
        InlineKeyboardButton("45 daq", callback_data="duration:45"),
        InlineKeyboardButton("90 daq", callback_data="duration:90"),
        InlineKeyboardButton("120 daq", callback_data="duration:120")
    )
    keyboard.add(
        InlineKeyboardButton("180 daq", callback_data="duration:180"),
        InlineKeyboardButton("Cheksiz", callback_data="duration:1440")
    )
    
    return keyboard


def report_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("📅 Haftalik hisobot", callback_data="report:weekly"),
        InlineKeyboardButton("📆 Oylik hisobot", callback_data="report:monthly"),
        InlineKeyboardButton("📊 To'liq hisobot", callback_data="report:full")
    )
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_attendance"))
    
    return keyboard


def confirm_registration_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_reg"),
        InlineKeyboardButton("✏️ O'zgartirish", callback_data="edit_reg")
    )
    keyboard.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_reg"))
    
    return keyboard


def my_attendance_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("📅 Bu hafta", callback_data="my_att:week"),
        InlineKeyboardButton("📆 Bu oy", callback_data="my_att:month"),
        InlineKeyboardButton("📊 Umumiy", callback_data="my_att:all")
    )
    keyboard.add(InlineKeyboardButton("📥 Excel yuklab olish", callback_data="my_att:excel"))
    
    return keyboard


def back_button(callback: str = "back") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=callback))
    return keyboard
