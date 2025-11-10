from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from states.message_states import MessageStates
from keyboards.default.menu import confirm_message_menu, user_menu
from data.config import ADMINS


# Xabar yozish tugmasi bosilganda
@dp.message_handler(text="✍️ Xabar yozish")
async def write_message(message: types.Message):
    await message.answer(
        "📝 Iltimos, o'z fikr va takliflaringizni yozing:\n\n"
        "Xabaringizni yozib tugatsangiz, uni tasdiqlash uchun ko'rsatamiz.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await MessageStates.waiting_for_message.set()


# Xabar qabul qilish
@dp.message_handler(state=MessageStates.waiting_for_message, content_types=types.ContentTypes.ANY)
async def receive_message(message: types.Message, state: FSMContext):
    # Xabarni state'ga saqlash
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
    
    # Xabarni qaytarib ko'rsatish
    await message.answer("📬 Sizning xabaringiz:")
    
    if message.text:
        await message.answer(message.text)
    elif message.photo:
        await message.answer_photo(message.photo[-1].file_id, caption=message.caption)
    elif message.video:
        await message.answer_video(message.video.file_id, caption=message.caption)
    elif message.document:
        await message.answer_document(message.document.file_id, caption=message.caption)
    elif message.voice:
        await message.answer_voice(message.voice.file_id)
    elif message.audio:
        await message.answer_audio(message.audio.file_id, caption=message.caption)
    
    await message.answer(
        "❓ Xabarni tasdiqlaysizmi?\n\n"
        "✅ Tasdiqlash - xabar rektorga yuboriladi\n"
        "✏️ Yangilash - xabarni qayta yozish\n"
        "❌ Bekor qilish - xabarni yubormaslik",
        reply_markup=confirm_message_menu()
    )
    await MessageStates.confirm_message.set()


# Xabarni tasdiqlash
@dp.message_handler(text="✅ Tasdiqlash", state=MessageStates.confirm_message)
async def confirm_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content_type = data.get('content_type')
    
    # Foydalanuvchi ma'lumotlari
    user_info = (
        f"👤 <b>Yangi xabar:</b>\n"
        f"Ism: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username if message.from_user.username else 'Yoq'}\n"
        f"ID: <code>{message.from_user.id}</code>\n"
        f"{'-' * 30}\n"
    )
    
    # Adminlarga xabar yuborish
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, user_info)
            
            if content_type == 'text':
                await bot.send_message(admin_id, data['text'])
            elif content_type == 'photo':
                await bot.send_photo(admin_id, data['photo'], caption=data.get('caption'))
            elif content_type == 'video':
                await bot.send_video(admin_id, data['video'], caption=data.get('caption'))
            elif content_type == 'document':
                await bot.send_document(admin_id, data['document'], caption=data.get('caption'))
            elif content_type == 'voice':
                await bot.send_voice(admin_id, data['voice'])
            elif content_type == 'audio':
                await bot.send_audio(admin_id, data['audio'], caption=data.get('caption'))
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xato: {e}")
    
    await message.answer(
        "✅ Xabaringiz muvaffaqiyatli yuborildi!\n"
        "Rektorat tez orada ko'rib chiqadi.",
        reply_markup=user_menu()
    )
    await state.finish()


# Xabarni yangilash
@dp.message_handler(text="✏️ Yangilash", state=MessageStates.confirm_message)
async def update_message(message: types.Message):
    await message.answer(
        "📝 Xabaringizni qayta yozing:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await MessageStates.waiting_for_message.set()


# Xabarni bekor qilish
@dp.message_handler(text="❌ Bekor qilish", state=MessageStates.confirm_message)
async def cancel_message(message: types.Message, state: FSMContext):
    await message.answer(
        "❌ Xabar yuborish bekor qilindi.",
        reply_markup=user_menu()
    )
    await state.finish()
