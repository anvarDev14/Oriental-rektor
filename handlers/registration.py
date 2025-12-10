"""
Talaba ro'yxatdan o'tish handleri
"""
from aiogram import types
from aiogram.dispatcher import FSMContext

from states.attendance_states import StudentRegistration
from keyboards.attendance_kb import (
    directions_keyboard, groups_keyboard, phone_keyboard,
    cancel_keyboard, confirm_registration_keyboard, user_main_menu
)
from utils.attendance_db import AttendanceDB


async def start_registration(message: types.Message, state: FSMContext):
    db = AttendanceDB()

    if db.is_student_registered(message.from_user.id):
        student = db.get_student(message.from_user.id)
        await message.answer(
            f"✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            f"👤 Ism: {student['full_name']}\n"
            f"🆔 ID: {student['student_id']}\n"
            f"📚 Yo'nalish: {student['direction']}\n"
            f"👥 Guruh: {student['group_name']}",
            reply_markup=user_main_menu(is_registered=True)
        )
        return

    await message.answer(
        "📋 <b>Ro'yxatdan o'tish</b>\n\n"
        "Iltimos, to'liq ismingizni kiriting:\n"
        "<i>(Masalan: Aliyev Ali Valiyevich)</i>",
        reply_markup=cancel_keyboard()
    )
    await StudentRegistration.full_name.set()


async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=user_main_menu())
        return

    full_name = message.text.strip()
    if len(full_name) < 5:
        await message.answer("⚠️ Iltimos, to'liq ismingizni kiriting!")
        return

    await state.update_data(full_name=full_name)
    await message.answer(
        "🆔 <b>Talaba ID raqamingizni kiriting:</b>\n"
        "<i>(Masalan: ST2024001)</i>",
        reply_markup=cancel_keyboard()
    )
    await StudentRegistration.student_id.set()


async def process_student_id(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=user_main_menu())
        return

    student_id = message.text.strip().upper()
    await state.update_data(student_id=student_id)

    db = AttendanceDB()
    directions = db.get_all_directions()

    await message.answer(
        "📚 <b>Yo'nalishingizni tanlang:</b>",
        reply_markup=directions_keyboard(directions, "reg_dir")
    )
    await StudentRegistration.direction.set()


async def process_direction_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        await callback.message.edit_text("❌ Bekor qilindi.")
        return

    direction = callback.data.split(":")[1]
    await state.update_data(direction=direction)

    db = AttendanceDB()
    groups = db.get_groups_by_direction(direction)

    if not groups:
        default_groups = ["101", "102", "103", "201", "202", "203"]
        for g in default_groups:
            db.add_group(g, direction)
        groups = default_groups

    await callback.message.edit_text(
        f"📚 Yo'nalish: <b>{direction}</b>\n\n"
        "👥 <b>Guruhingizni tanlang:</b>",
        reply_markup=groups_keyboard(groups, direction, "reg_grp")
    )
    await StudentRegistration.group.set()


async def process_group_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        await callback.message.edit_text("❌ Bekor qilindi.")
        return

    if callback.data == "back_to_directions":
        db = AttendanceDB()
        directions = db.get_all_directions()
        await callback.message.edit_text(
            "📚 <b>Yo'nalishingizni tanlang:</b>",
            reply_markup=directions_keyboard(directions, "reg_dir")
        )
        await StudentRegistration.direction.set()
        return

    parts = callback.data.split(":")
    group = parts[2]
    await state.update_data(group_name=group)

    await callback.message.delete()
    await callback.message.answer(
        "📱 <b>Telefon raqamingizni yuboring:</b>\n<i>(Ixtiyoriy)</i>",
        reply_markup=phone_keyboard()
    )
    await StudentRegistration.phone.set()


async def process_phone(message: types.Message, state: FSMContext):
    phone = None

    if message.contact:
        phone = message.contact.phone_number
    elif message.text == "⏭ O'tkazib yuborish":
        phone = None
    elif message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=user_main_menu())
        return
    else:
        phone = message.text.strip()

    await state.update_data(phone=phone)
    data = await state.get_data()

    # Telefon uchun alohida o'zgaruvchi
    phone_display = phone if phone else "Ko'rsatilmagan"

    text = (
        "📋 <b>Ma'lumotlaringizni tasdiqlang:</b>\n\n"
        f"👤 Ism: <b>{data['full_name']}</b>\n"
        f"🆔 ID: <b>{data['student_id']}</b>\n"
        f"📚 Yo'nalish: <b>{data['direction']}</b>\n"
        f"👥 Guruh: <b>{data['group_name']}</b>\n"
        f"📱 Telefon: <b>{phone_display}</b>\n\n"
        "✅ Tasdiqlaysizmi?"
    )

    await message.answer(text, reply_markup=confirm_registration_keyboard())
    await StudentRegistration.confirm.set()


async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel_reg":
        await state.finish()
        await callback.message.edit_text("❌ Bekor qilindi.")
        await callback.message.answer("Bosh menyu:", reply_markup=user_main_menu())
        return

    if callback.data == "edit_reg":
        await callback.message.edit_text(
            "📋 <b>Ro'yxatdan o'tish</b>\n\nIltimos, to'liq ismingizni kiriting:"
        )
        await StudentRegistration.full_name.set()
        return

    data = await state.get_data()
    db = AttendanceDB()

    success = db.register_student(
        user_id=callback.from_user.id,
        full_name=data['full_name'],
        student_id=data['student_id'],
        direction=data['direction'],
        group_name=data['group_name'],
        phone=data.get('phone')
    )

    await state.finish()

    if success:
        await callback.message.edit_text(
            "✅ <b>Tabriklaymiz!</b>\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            "Endi QR kod skanerlab davomat qilishingiz mumkin."
        )
        await callback.message.answer("Bosh menyu:", reply_markup=user_main_menu(is_registered=True))
    else:
        await callback.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")


def register_registration_handlers(dp):
    dp.register_message_handler(start_registration, text="📋 Ro'yxatdan o'tish")
    dp.register_message_handler(process_full_name, state=StudentRegistration.full_name)
    dp.register_message_handler(process_student_id, state=StudentRegistration.student_id)
    dp.register_callback_query_handler(
        process_direction_choice,
        lambda c: c.data.startswith("reg_dir:") or c.data == "cancel",
        state=StudentRegistration.direction
    )
    dp.register_callback_query_handler(
        process_group_choice,
        lambda c: c.data.startswith("reg_grp:") or c.data in ["cancel", "back_to_directions"],
        state=StudentRegistration.group
    )
    dp.register_message_handler(
        process_phone,
        state=StudentRegistration.phone,
        content_types=[types.ContentType.CONTACT, types.ContentType.TEXT]
    )
    dp.register_callback_query_handler(
        confirm_registration,
        lambda c: c.data in ["confirm_reg", "edit_reg", "cancel_reg"],
        state=StudentRegistration.confirm
    )