import asyncio
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from filters.is_admin import IsAdmin
from states.message_states import BroadcastStates
from keyboards.inline.admin_keyboard import broadcast_type_keyboard, broadcast_time_keyboard, confirm_broadcast_keyboard
from keyboards.default.menu import cancel_menu, admin_menu
from utils.db_api.database import Database


@dp.message_handler(IsAdmin(), text="📢 Reklama yuborish")
async def start_broadcast(message: types.Message):
    await message.answer(
        "📢 <b>Reklama yuborish</b>\n\n"
        "Qanday turdagi reklama yubormoqchisiz?",
        reply_markup=broadcast_type_keyboard()
    )


@dp.callback_query_handler(text="broadcast_text")
async def broadcast_text_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = 'text'
    
    await call.message.edit_text(
        "📝 Reklama xabarini yuboring:\n\n"
        "Matn, rasm, video, audio va boshqa formatlarni yuborishingiz mumkin."
    )
    await BroadcastStates.waiting_for_content.set()
    await call.answer()


@dp.callback_query_handler(text="broadcast_forward")
async def broadcast_forward_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = 'forward'
    
    await call.message.edit_text(
        "🔄 Forward qilmoqchi bo'lgan xabarni yuboring:\n\n"
        "Biror kanaldan yoki chatdan xabarni forward qiling."
    )
    await BroadcastStates.waiting_for_content.set()
    await call.answer()


@dp.message_handler(IsAdmin(), state=BroadcastStates.waiting_for_content, content_types=types.ContentTypes.ANY)
async def receive_broadcast_content(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_id'] = message.message_id
        data['chat_id'] = message.chat.id
        data['content_type'] = message.content_type
        
        if message.text:
            data['text'] = message.text
        elif message.photo:
            data['photo'] = message.photo[-1].file_id
            data['caption'] = message.caption
        elif message.video:
            data['video'] = message.video.file_id
            data['caption'] = message.caption
        elif message.document:
            data['document'] = message.document.file_id
            data['caption'] = message.caption
        elif message.voice:
            data['voice'] = message.voice.file_id
        elif message.audio:
            data['audio'] = message.audio.file_id
            data['caption'] = message.caption
        elif message.animation:
            data['animation'] = message.animation.file_id
            data['caption'] = message.caption
        elif message.video_note:
            data['video_note'] = message.video_note.file_id
        elif message.sticker:
            data['sticker'] = message.sticker.file_id
    
    await message.answer(
        "⏰ Reklamani qachon yuborish kerak?",
        reply_markup=broadcast_time_keyboard()
    )


@dp.callback_query_handler(text="time_now", state=BroadcastStates.waiting_for_content)
async def broadcast_now(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['send_time'] = 'now'
    
    await call.message.edit_text(
        "📢 Reklama hozir yuborilsinmi?\n\n"
        "✅ Tasdiqlash uchun \"Yuborish\" tugmasini bosing.",
        reply_markup=confirm_broadcast_keyboard()
    )
    await call.answer()


@dp.callback_query_handler(text="time_later", state=BroadcastStates.waiting_for_content)
async def broadcast_later(call: types.CallbackQuery, state: FSMContext):
    """Keyinroq yuborish uchun vaqt so'rash"""

    # Eski xabarni o'chirish
    try:
        await call.message.delete()
    except:
        pass

    # Yangi xabar yuborish
    await call.message.answer(
        "⏳ <b>Reklama qachon yuborilsin?</b>\n\n"
        "Quyidagi formatda yozing:\n"
        "• <code>5m</code> - 5 daqiqadan keyin\n"
        "• <code>30m</code> - 30 daqiqadan keyin\n"
        "• <code>2h</code> - 2 soatdan keyin\n"
        "• <code>1d</code> - 1 kundan keyin\n"
        "• <code>1w</code> - 1 haftadan keyin\n\n"
        "💡 <b>Misol:</b> <code>15m</code>, <code>3h</code>, <code>2d</code>",
        reply_markup=cancel_menu()
    )

    await BroadcastStates.waiting_for_time.set()
    await call.answer()

@dp.message_handler(IsAdmin(), state=BroadcastStates.waiting_for_time)
async def receive_time(message: types.Message, state: FSMContext):
    time_input = message.text.strip().lower()
    
    if time_input == "❌ bekor qilish":
        await message.answer("❌ Reklama yuborish bekor qilindi.", reply_markup=admin_menu())
        await state.finish()
        return
    
    try:
        if time_input.endswith('m'):
            minutes = int(time_input[:-1])
            send_datetime = datetime.now() + timedelta(minutes=minutes)
            time_text = f"{minutes} daqiqa"
        elif time_input.endswith('h'):
            hours = int(time_input[:-1])
            send_datetime = datetime.now() + timedelta(hours=hours)
            time_text = f"{hours} soat"
        elif time_input.endswith('d'):
            days = int(time_input[:-1])
            send_datetime = datetime.now() + timedelta(days=days)
            time_text = f"{days} kun"
        elif time_input.endswith('w'):
            weeks = int(time_input[:-1])
            send_datetime = datetime.now() + timedelta(weeks=weeks)
            time_text = f"{weeks} hafta"
        else:
            await message.answer("❌ Noto'g'ri format! Masalan: 30m, 2h, 1d, 1w")
            return
        
        async with state.proxy() as data:
            data['send_time'] = send_datetime.timestamp()
            data['time_text'] = time_text
        
        await message.answer(
            f"📢 Reklama <b>{time_text}</b> dan keyin yuboriladi.\n\n"
            f"Yuborish vaqti: {send_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"✅ Tasdiqlaysizmi?",
            reply_markup=confirm_broadcast_keyboard()
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Masalan: 30m, 2h, 1d, 1w")


@dp.callback_query_handler(text="confirm_broadcast_yes", state=[BroadcastStates.waiting_for_content, BroadcastStates.waiting_for_time])
async def confirm_broadcast(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    db = Database()
    users = db.select_all_users()
    
    send_time = data.get('send_time', 'now')
    
    if send_time == 'now':
        await call.message.edit_text("📤 Reklama yuborilmoqda...")
        await send_broadcast(users, data)
        await call.message.edit_text(
            f"✅ Reklama muvaffaqiyatli yuborildi!\n\n"
            f"📊 Jami: {len(users)} ta foydalanuvchi"
        )
    else:
        send_datetime = datetime.fromtimestamp(send_time)
        wait_seconds = (send_datetime - datetime.now()).total_seconds()
        
        await call.message.edit_text(
            f"⏳ Reklama rejalashtirildi!\n\n"
            f"📅 Yuborish vaqti: {send_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏰ Qolgan vaqt: {data.get('time_text')}"
        )
        
        asyncio.create_task(scheduled_broadcast(wait_seconds, users, data, call.message.chat.id))
    
    await state.finish()
    await call.answer("✅ Reklama yuborildi!")


async def scheduled_broadcast(wait_seconds, users, data, admin_chat_id):
    await asyncio.sleep(wait_seconds)
    await send_broadcast(users, data)
    await bot.send_message(
        admin_chat_id,
        f"✅ Reklama muvaffaqiyatli yuborildi!\n\n"
        f"📊 Jami: {len(users)} ta foydalanuvchi"
    )


async def send_broadcast(users, data):
    content_type = data.get('content_type')
    broadcast_type = data.get('type')
    success = 0
    failed = 0
    
    for user in users:
        user_id = user[0]
        try:
            if broadcast_type == 'forward':
                await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=data['chat_id'],
                    message_id=data['message_id']
                )
            else:
                if content_type == 'text':
                    await bot.send_message(user_id, data['text'])
                elif content_type == 'photo':
                    await bot.send_photo(user_id, data['photo'], caption=data.get('caption'))
                elif content_type == 'video':
                    await bot.send_video(user_id, data['video'], caption=data.get('caption'))
                elif content_type == 'document':
                    await bot.send_document(user_id, data['document'], caption=data.get('caption'))
                elif content_type == 'voice':
                    await bot.send_voice(user_id, data['voice'])
                elif content_type == 'audio':
                    await bot.send_audio(user_id, data['audio'], caption=data.get('caption'))
                elif content_type == 'animation':
                    await bot.send_animation(user_id, data['animation'], caption=data.get('caption'))
                elif content_type == 'video_note':
                    await bot.send_video_note(user_id, data['video_note'])
                elif content_type == 'sticker':
                    await bot.send_sticker(user_id, data['sticker'])
            
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1


@dp.callback_query_handler(text="confirm_broadcast_no", state=[BroadcastStates.waiting_for_content, BroadcastStates.waiting_for_time])
async def cancel_broadcast(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("❌ Reklama yuborish bekor qilindi.")
    await state.finish()
    await call.answer()


@dp.message_handler(IsAdmin(), text="❌ Bekor qilish", state=[BroadcastStates.waiting_for_content, BroadcastStates.waiting_for_time])
async def cancel_broadcast_state(message: types.Message, state: FSMContext):
    await message.answer("❌ Reklama yuborish bekor qilindi.", reply_markup=admin_menu())
    await state.finish()
