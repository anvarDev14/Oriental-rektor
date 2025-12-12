"""
Admin panel - Davomat boshqaruvi
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime

from states.attendance_states import CreateSession, AddDirection, AddGroup, ExportReport
from keyboards.attendance_kb import (
    attendance_admin_menu, directions_keyboard, groups_keyboard,
    duration_keyboard, session_actions, cancel_keyboard, back_button
)
from utils.attendance_db import AttendanceDB
from utils.qr_generator import generate_attendance_qr
from utils.excel_export import create_attendance_report
from config import BOT_USERNAME


async def open_attendance_menu(message: types.Message):
    await message.answer(
        "📋 <b>Davomat boshqaruvi</b>\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=attendance_admin_menu()
    )


async def attendance_menu_callback(callback: types.CallbackQuery):
    """Davomat menusiga qaytish"""
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "📋 <b>Davomat boshqaruvi</b>\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=attendance_admin_menu()
    )
    await callback.answer()


# ==================== YANGI DARS YARATISH ====================

async def start_new_session(callback: types.CallbackQuery, state: FSMContext):
    db = AttendanceDB()
    directions = db.get_all_directions()

    try:
        await callback.message.edit_text(
            "🆕 <b>Yangi dars yaratish</b>\n\n📚 Yo'nalishni tanlang:",
            reply_markup=directions_keyboard(directions, "session_dir")
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            "🆕 <b>Yangi dars yaratish</b>\n\n📚 Yo'nalishni tanlang:",
            reply_markup=directions_keyboard(directions, "session_dir")
        )

    await CreateSession.direction.set()


async def session_select_direction(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        try:
            await callback.message.edit_text("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        except:
            await callback.message.delete()
            await callback.message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    direction = callback.data.split(":")[1]
    await state.update_data(direction=direction)

    db = AttendanceDB()
    groups = db.get_groups_by_direction(direction)

    if not groups:
        await callback.answer("Bu yo'nalishda guruhlar yo'q!", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            f"📚 Yo'nalish: <b>{direction}</b>\n\n👥 Guruhni tanlang:",
            reply_markup=groups_keyboard(groups, direction, "session_grp")
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            f"📚 Yo'nalish: <b>{direction}</b>\n\n👥 Guruhni tanlang:",
            reply_markup=groups_keyboard(groups, direction, "session_grp")
        )

    await CreateSession.group.set()


async def session_select_group(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "back_to_directions":
        db = AttendanceDB()
        directions = db.get_all_directions()
        try:
            await callback.message.edit_text(
                "📚 Yo'nalishni tanlang:",
                reply_markup=directions_keyboard(directions, "session_dir")
            )
        except:
            await callback.message.delete()
            await callback.message.answer(
                "📚 Yo'nalishni tanlang:",
                reply_markup=directions_keyboard(directions, "session_dir")
            )
        await CreateSession.direction.set()
        return

    parts = callback.data.split(":")
    group = parts[2]
    await state.update_data(group_name=group)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "📝 <b>Fan nomini kiriting:</b>\n<i>(Masalan: Matematika, Fizika)</i>",
        reply_markup=cancel_keyboard()
    )
    await CreateSession.subject.set()


async def session_enter_subject(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    subject = message.text.strip()
    await state.update_data(subject=subject)

    await message.answer(
        f"📚 Fan: <b>{subject}</b>\n\n⏱ Dars davomiyligini tanlang:",
        reply_markup=duration_keyboard()
    )
    await CreateSession.duration.set()


async def session_select_duration(callback: types.CallbackQuery, state: FSMContext):
    duration = int(callback.data.split(":")[1])

    data = await state.get_data()
    db = AttendanceDB()

    session = db.create_session(
        subject=data['subject'],
        direction=data['direction'],
        group_name=data['group_name'],
        teacher_name=callback.from_user.full_name,
        duration_minutes=duration,
        created_by=callback.from_user.id
    )

    await state.finish()

    qr_image = generate_attendance_qr(
        bot_username=BOT_USERNAME,
        qr_token=session['qr_token'],
        subject=session['subject'],
        group=session['group_name'],
        direction=session['direction']
    )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        types.InputFile(qr_image, filename="qr_code.png"),
        caption=(
            f"✅ <b>Dars sessiyasi yaratildi!</b>\n\n"
            f"📚 Fan: {session['subject']}\n"
            f"🎓 Yo'nalish: {session['direction']}\n"
            f"👥 Guruh: {session['group_name']}\n"
            f"📅 Kun: {session['day_of_week']}\n"
            f"⏱ Amal qilish: {duration} daqiqa\n\n"
            f"🔗 Link: https://t.me/{BOT_USERNAME}?start=att_{session['qr_token']}\n\n"
            f"📱 Talabalar QR skanerlab davomat qiladi."
        ),
        reply_markup=session_actions(session['session_id'])
    )


# ==================== FAOL SESSIYALAR ====================

async def show_active_sessions(callback: types.CallbackQuery):
    db = AttendanceDB()
    sessions = db.get_active_sessions()

    # Avval eski xabarni o'chiramiz
    try:
        await callback.message.delete()
    except:
        pass

    if not sessions:
        await callback.message.answer(
            "📋 <b>Faol darslar</b>\n\nHozirda faol darslar yo'q.",
            reply_markup=back_button("back_to_attendance")
        )
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(row_width=1)

    for session in sessions[:10]:
        keyboard.add(
            InlineKeyboardButton(
                f"📚 {session['subject']} | {session['group_name']} | {session['session_date']}",
                callback_data=f"view_session:{session['session_id']}"
            )
        )

    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_attendance"))

    await callback.message.answer(
        f"📋 <b>Faol darslar ({len(sessions)} ta)</b>\n\nKo'rish uchun tanlang:",
        reply_markup=keyboard
    )
    await callback.answer()


async def view_session_details(callback: types.CallbackQuery):
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    session = db.get_session_by_id(session_id)
    attendance = db.get_session_attendance(session_id)

    if attendance:
        students_text = "\n".join([f"✅ {a['full_name']}" for a in attendance])
        count = len(attendance)
    else:
        students_text = "Hali hech kim davomat qilmagan"
        count = 0

    subject_name = session['subject'] if session else "Nomalum"

    # Avval eski xabarni o'chiramiz
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📋 <b>Dars: {subject_name}</b>\n\n"
        f"👥 Kelganlar soni: {count}\n\n{students_text}",
        reply_markup=session_actions(session_id)
    )
    await callback.answer()


async def close_session(callback: types.CallbackQuery):
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    db.close_session(session_id)

    await callback.answer("✅ Dars yopildi!", show_alert=True)
    await show_active_sessions(callback)


async def refresh_session_qr(callback: types.CallbackQuery):
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    session = db.get_session_by_id(session_id)

    if not session:
        await callback.answer("Sessiya topilmadi!", show_alert=True)
        return

    qr_image = generate_attendance_qr(
        bot_username=BOT_USERNAME,
        qr_token=session['qr_token'],
        subject=session['subject'],
        group=session['group_name'],
        direction=session['direction']
    )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        types.InputFile(qr_image, filename="qr_code.png"),
        caption=(
            f"📚 Fan: {session['subject']}\n"
            f"👥 Guruh: {session['group_name']}\n"
            f"🔗 Link: https://t.me/{BOT_USERNAME}?start=att_{session['qr_token']}"
        ),
        reply_markup=session_actions(session_id)
    )
    await callback.answer()


# ==================== SESSION ATTENDANCE (Davomat tugmasi) ====================

async def show_session_attendance(callback: types.CallbackQuery):
    """📊 Davomat tugmasi - sessiya davomatini ko'rsatish"""
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

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Yangilash", callback_data=f"session_att:{session_id}"),
        InlineKeyboardButton("📥 Excel", callback_data=f"export_session:{session_id}")
    )
    keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"back_to_qr:{session_id}"))

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


async def back_to_qr(callback: types.CallbackQuery):
    """QR kodga qaytish"""
    session_id = callback.data.split(":")[1]

    db = AttendanceDB()
    session = db.get_session_by_id(session_id)

    if not session:
        await callback.answer("Sessiya topilmadi!", show_alert=True)
        return

    qr_image = generate_attendance_qr(
        bot_username=BOT_USERNAME,
        qr_token=session['qr_token'],
        subject=session['subject'],
        group=session['group_name'],
        direction=session['direction']
    )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        types.InputFile(qr_image, filename="qr_code.png"),
        caption=(
            f"📚 Fan: {session['subject']}\n"
            f"🎓 Yo'nalish: {session['direction']}\n"
            f"👥 Guruh: {session['group_name']}\n"
            f"📅 Kun: {session['day_of_week']}\n"
            f"🔗 Link: https://t.me/{BOT_USERNAME}?start=att_{session['qr_token']}"
        ),
        reply_markup=session_actions(session['session_id'])
    )
    await callback.answer()


# ==================== HISOBOTLAR ====================

async def start_report_export(callback: types.CallbackQuery, state: FSMContext):
    db = AttendanceDB()
    directions = db.get_all_directions()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "📊 <b>Hisobot olish</b>\n\n📚 Yo'nalishni tanlang:",
        reply_markup=directions_keyboard(directions, "report_dir")
    )
    await ExportReport.direction.set()


async def report_select_direction(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    direction = callback.data.split(":")[1]
    await state.update_data(direction=direction)

    db = AttendanceDB()
    groups = db.get_groups_by_direction(direction)

    try:
        await callback.message.edit_text(
            f"📚 Yo'nalish: <b>{direction}</b>\n\n👥 Guruhni tanlang:",
            reply_markup=groups_keyboard(groups, direction, "report_grp")
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            f"📚 Yo'nalish: <b>{direction}</b>\n\n👥 Guruhni tanlang:",
            reply_markup=groups_keyboard(groups, direction, "report_grp")
        )

    await ExportReport.group.set()


async def report_select_group(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "back_to_directions":
        db = AttendanceDB()
        directions = db.get_all_directions()
        try:
            await callback.message.edit_text(
                "📚 Yo'nalishni tanlang:",
                reply_markup=directions_keyboard(directions, "report_dir")
            )
        except:
            await callback.message.delete()
            await callback.message.answer(
                "📚 Yo'nalishni tanlang:",
                reply_markup=directions_keyboard(directions, "report_dir")
            )
        await ExportReport.direction.set()
        return

    parts = callback.data.split(":")
    group = parts[2]

    data = await state.get_data()
    direction = data['direction']

    await state.finish()

    db = AttendanceDB()
    report_data = db.get_weekly_report(direction, group)

    if not report_data['students']:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(
            "⚠️ Bu guruhda talabalar yo'q!",
            reply_markup=attendance_admin_menu()
        )
        return

    excel_file = create_attendance_report(report_data)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_document(
        types.InputFile(
            excel_file,
            filename=f"davomat_{direction}_{group}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        ),
        caption=(
            f"📊 <b>Davomat hisoboti</b>\n\n"
            f"📚 Yo'nalish: {direction}\n"
            f"👥 Guruh: {group}\n"
            f"📅 Davr: {report_data['week_start']} - {report_data['week_end']}"
        ),
        reply_markup=attendance_admin_menu()
    )


async def export_session_excel(callback: types.CallbackQuery):
    """📥 Excel tugmasi - sessiya davomatini Excel ga eksport"""
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


# ==================== STATISTIKA ====================

async def show_attendance_stats(callback: types.CallbackQuery):
    db = AttendanceDB()
    stats = db.get_attendance_stats()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📈 <b>Davomat statistikasi</b>\n\n"
        f"👥 Ro'yxatdagi talabalar: {stats['total_students']}\n"
        f"📚 Jami darslar: {stats['total_sessions']}\n"
        f"✅ Jami davomat: {stats['total_present']}\n",
        reply_markup=back_button("back_to_attendance")
    )
    await callback.answer()


# ==================== YO'NALISH/GURUH QO'SHISH ====================

async def start_add_direction(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "➕ <b>Yangi yo'nalish qo'shish</b>\n\nYo'nalish nomini kiriting:",
        reply_markup=cancel_keyboard()
    )
    await AddDirection.name.set()


async def add_direction_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    db = AttendanceDB()
    success = db.add_direction(message.text.strip())

    await state.finish()

    if success:
        await message.answer(f"✅ Yo'nalish qo'shildi: <b>{message.text}</b>", reply_markup=attendance_admin_menu())
    else:
        await message.answer("❌ Bu yo'nalish allaqachon mavjud!", reply_markup=attendance_admin_menu())


async def start_add_group(callback: types.CallbackQuery, state: FSMContext):
    db = AttendanceDB()
    directions = db.get_all_directions()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "➕ <b>Yangi guruh qo'shish</b>\n\nAvval yo'nalishni tanlang:",
        reply_markup=directions_keyboard(directions, "addgrp_dir")
    )
    await AddGroup.direction.set()


async def add_group_direction(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    direction = callback.data.split(":")[1]
    await state.update_data(direction=direction)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        f"📚 Yo'nalish: <b>{direction}</b>\n\nGuruh nomini kiriting (masalan: 101):",
        reply_markup=cancel_keyboard()
    )
    await AddGroup.name.set()


async def add_group_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.finish()
        await message.answer("❌ Bekor qilindi.", reply_markup=attendance_admin_menu())
        return

    data = await state.get_data()
    db = AttendanceDB()
    success = db.add_group(message.text.strip(), data['direction'])

    await state.finish()

    if success:
        await message.answer(
            f"✅ Guruh qo'shildi: <b>{data['direction']} - {message.text}</b>",
            reply_markup=attendance_admin_menu()
        )
    else:
        await message.answer("❌ Bu guruh allaqachon mavjud!", reply_markup=attendance_admin_menu())


def register_admin_handlers(dp, admin_filter=None):
    dp.register_message_handler(open_attendance_menu, text="📋 Davomat")
    dp.register_callback_query_handler(attendance_menu_callback, text="back_to_attendance")

    # Session yaratish
    dp.register_callback_query_handler(start_new_session, text="new_session", state="*")
    dp.register_callback_query_handler(
        session_select_direction,
        lambda c: c.data.startswith("session_dir:") or c.data == "cancel",
        state=CreateSession.direction
    )
    dp.register_callback_query_handler(
        session_select_group,
        lambda c: c.data.startswith("session_grp:") or c.data == "back_to_directions",
        state=CreateSession.group
    )
    dp.register_message_handler(session_enter_subject, state=CreateSession.subject)
    dp.register_callback_query_handler(
        session_select_duration,
        lambda c: c.data.startswith("duration:"),
        state=CreateSession.duration
    )

    # Faol sessiyalar
    dp.register_callback_query_handler(show_active_sessions, text="active_sessions")
    dp.register_callback_query_handler(view_session_details, lambda c: c.data.startswith("view_session:"))
    dp.register_callback_query_handler(close_session, lambda c: c.data.startswith("close_session:"))
    dp.register_callback_query_handler(refresh_session_qr, lambda c: c.data.startswith("refresh_qr:"))

    # Session davomat va Excel
    dp.register_callback_query_handler(show_session_attendance, lambda c: c.data.startswith("session_att:"))
    dp.register_callback_query_handler(export_session_excel, lambda c: c.data.startswith("export_session:"))
    dp.register_callback_query_handler(back_to_qr, lambda c: c.data.startswith("back_to_qr:"))

    # Hisobotlar
    dp.register_callback_query_handler(start_report_export, text="get_report", state="*")
    dp.register_callback_query_handler(
        report_select_direction,
        lambda c: c.data.startswith("report_dir:") or c.data == "cancel",
        state=ExportReport.direction
    )
    dp.register_callback_query_handler(
        report_select_group,
        lambda c: c.data.startswith("report_grp:") or c.data == "back_to_directions",
        state=ExportReport.group
    )

    # Statistika
    dp.register_callback_query_handler(show_attendance_stats, text="attendance_stats")

    # Yo'nalish qo'shish
    dp.register_callback_query_handler(start_add_direction, text="add_direction", state="*")
    dp.register_message_handler(add_direction_name, state=AddDirection.name)

    # Guruh qo'shish
    dp.register_callback_query_handler(start_add_group, text="add_group", state="*")
    dp.register_callback_query_handler(
        add_group_direction,
        lambda c: c.data.startswith("addgrp_dir:") or c.data == "cancel",
        state=AddGroup.direction
    )
    dp.register_message_handler(add_group_name, state=AddGroup.name)