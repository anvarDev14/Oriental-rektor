"""
QR kod orqali davomat handleri
Deep link: https://t.me/botname?start=att_QRTOKEN
"""
from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.attendance_db import AttendanceDB
from keyboards.attendance_kb import user_main_menu, my_attendance_keyboard
from utils.excel_export import create_student_report


async def handle_attendance_deeplink(message: types.Message, state: FSMContext = None):
    """QR kod skanerlanganda ishlaydigan handler"""
    args = message.get_args()

    if not args or not args.startswith("att_"):
        return False

    qr_token = args[4:]
    db = AttendanceDB()
    user_id = message.from_user.id

    if not db.is_student_registered(user_id):
        await message.answer(
            "⚠️ <b>Siz hali ro'yxatdan o'tmagansiz!</b>\n\n"
            "Davomat qilish uchun avval ro'yxatdan o'ting.\n\n"
            "📋 <b>Ro'yxatdan o'tish</b> tugmasini bosing.",
            reply_markup=user_main_menu(is_registered=False)
        )
        return True

    result = db.mark_attendance(user_id, qr_token)

    if result["success"]:
        student = db.get_student(user_id)
        await message.answer(
            "✅ <b>Davomat muvaffaqiyatli belgilandi!</b>\n\n"
            f"👤 Talaba: {student['full_name']}\n"
            f"📚 Fan: {result['subject']}\n"
            f"📅 Sana: {result['session_date']}\n"
            f"🗓 Kun: {result['day_of_week']}\n\n"
            "🎓 Darsda yaxshi o'qing!",
            reply_markup=user_main_menu(is_registered=True)
        )
    else:
        error = result["error"]

        if error == "not_registered":
            await message.answer(
                "⚠️ <b>Siz hali ro'yxatdan o'tmagansiz!</b>",
                reply_markup=user_main_menu(is_registered=False)
            )
        else:
            await message.answer(
                f"❌ <b>Xatolik:</b> {error}",
                reply_markup=user_main_menu(is_registered=True)
            )

    return True


async def show_my_attendance(message: types.Message):
    db = AttendanceDB()
    user_id = message.from_user.id

    if not db.is_student_registered(user_id):
        await message.answer("⚠️ Avval ro'yxatdan o'ting!", reply_markup=user_main_menu(is_registered=False))
        return

    student = db.get_student(user_id)
    attendance = db.get_student_attendance(user_id)

    if not attendance:
        await message.answer(
            "📊 <b>Sizning davomatingiz</b>\n\nHozircha davomat yozuvlari yo'q.",
            reply_markup=user_main_menu(is_registered=True)
        )
        return

    present = sum(1 for a in attendance if a["status"] == "present")
    absent = sum(1 for a in attendance if a["status"] == "absent")
    total = present + absent
    percentage = (present / total * 100) if total > 0 else 0

    recent = attendance[:5]
    recent_text = ""
    for a in recent:
        status_emoji = "✅" if a["status"] == "present" else "❌"
        recent_text += f"{status_emoji} {a['date']} - {a['subject']}\n"

    text = (
        f"📊 <b>Sizning davomatingiz</b>\n\n"
        f"👤 {student['full_name']}\n"
        f"📚 {student['direction']} | {student['group_name']}\n\n"
        f"<b>📈 Statistika:</b>\n"
        f"✅ Kelgan: {present} marta\n"
        f"❌ Kelmagan: {absent} marta\n"
        f"📊 Davomat: <b>{percentage:.1f}%</b>\n\n"
        f"<b>📅 Oxirgi darslar:</b>\n{recent_text}"
    )

    await message.answer(text, reply_markup=my_attendance_keyboard())


async def export_my_attendance(callback: types.CallbackQuery):
    db = AttendanceDB()
    user_id = callback.from_user.id

    student = db.get_student(user_id)
    attendance = db.get_student_attendance(user_id)

    if not attendance:
        await callback.answer("Davomat yozuvlari yo'q!", show_alert=True)
        return

    excel_file = create_student_report(student, attendance)

    await callback.message.answer_document(
        types.InputFile(excel_file, filename=f"davomat_{student['student_id']}.xlsx"),
        caption=f"📊 {student['full_name']} - Davomat hisoboti"
    )
    await callback.answer()


async def show_my_info(message: types.Message):
    db = AttendanceDB()
    user_id = message.from_user.id

    student = db.get_student(user_id)

    if not student:
        await message.answer("⚠️ Siz ro'yxatdan o'tmagansiz!", reply_markup=user_main_menu(is_registered=False))
        return

    # F-string ichida backslash ishlatmaslik uchun
    phone_display = student['phone'] if student['phone'] else "Ko'rsatilmagan"
    reg_date = student['registered_at'][:10]

    await message.answer(
        f"👤 <b>Sizning ma'lumotlaringiz</b>\n\n"
        f"📝 Ism: {student['full_name']}\n"
        f"🆔 ID: {student['student_id']}\n"
        f"📚 Yo'nalish: {student['direction']}\n"
        f"👥 Guruh: {student['group_name']}\n"
        f"📱 Telefon: {phone_display}\n"
        f"📅 Ro'yxatdan o'tgan: {reg_date}",
        reply_markup=user_main_menu(is_registered=True)
    )


def register_attendance_handlers(dp):
    dp.register_message_handler(show_my_attendance, text="📊 Mening davomatim")
    dp.register_message_handler(show_my_info, text="👤 Mening ma'lumotlarim")
    dp.register_callback_query_handler(export_my_attendance, text="my_att:excel")