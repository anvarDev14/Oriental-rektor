from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def check_subscription_keyboard(channels):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        markup.add(InlineKeyboardButton(
            text=f"📢 {channel['name']}",
            url=channel['url']
        ))
    markup.add(InlineKeyboardButton(
        text="✅ Obunani tekshirish",
        callback_data="check_subscription"
    ))
    return markup


def broadcast_type_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📝 Oddiy xabar", callback_data="broadcast_text"),
        InlineKeyboardButton("🔄 Forward", callback_data="broadcast_forward")
    )
    return markup


def broadcast_time_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⏰ Hozir", callback_data="time_now"),
        InlineKeyboardButton("⏳ Keyinroq", callback_data="time_later")
    )
    return markup


def confirm_broadcast_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Yuborish", callback_data="confirm_broadcast_yes"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="confirm_broadcast_no")
    )
    return markup


def channel_actions_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
        InlineKeyboardButton("🗑 Kanal o'chirish", callback_data="delete_channel")
    )
    markup.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_admin"))
    return markup


def delete_channel_keyboard(channels):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        markup.add(InlineKeyboardButton(
            text=f"🗑 {channel[2]}",
            callback_data=f"del_channel_{channel[1]}"
        ))
    markup.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_channels"))
    return markup
