from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from loader import bot
from utils.db_api.database import Database
from keyboards.inline.admin_keyboard import check_subscription_keyboard
from data.config import ADMINS


class CheckSubscription(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        """Har bir message uchun tekshirish"""
        user_id = message.from_user.id

        # Adminlarni o'tkazib yuborish
        if str(user_id) in ADMINS:
            return

        db = Database()
        channels = db.get_all_channels()

        # Agar kanallar yo'q bo'lsa, o'tkazib yuborish
        if not channels:
            return

        not_subscribed = []

        # Har bir kanalni tekshirish
        for channel in channels:
            channel_id = channel[1]  # channel_id
            channel_name = channel[2]  # channel_name
            channel_url = channel[3]  # channel_url

            try:
                member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                # Agar user kanalda emas yoki kicklangan bo'lsa
                if member.status in ['left', 'kicked']:
                    not_subscribed.append({
                        'name': channel_name,
                        'url': channel_url
                    })
            except Exception as e:
                print(f"❌ Kanal tekshirishda xato ({channel_name}): {e}")
                # Xato bo'lsa ham davom etish
                continue

        # Agar obuna bo'lmagan kanallar bo'lsa
        if not_subscribed:
            text = (
                "❌ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart!</b>\n\n"
                "📢 <b>Majburiy kanallar:</b>\n"
            )

            for idx, channel in enumerate(not_subscribed, 1):
                text += f"{idx}. {channel['name']}\n"

            text += "\n👇 Quyidagi tugmalardan kanalga o'ting va <b>obuna</b> bo'ling, keyin <b>\"✅ Obunani tekshirish\"</b> tugmasini bosing."

            await message.answer(
                text,
                reply_markup=check_subscription_keyboard(not_subscribed)
            )

            # Keyingi handlerlarni to'xtatish
            raise CancelHandler()

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        """Callback query uchun tekshirish"""

        # Faqat check_subscription uchun
        if call.data == "check_subscription":
            user_id = call.from_user.id

            # Adminlar uchun
            if str(user_id) in ADMINS:
                await call.answer("✅ Siz adminsiz!", show_alert=True)
                await call.message.delete()
                return

            db = Database()
            channels = db.get_all_channels()

            if not channels:
                await call.answer("Majburiy kanallar yo'q!")
                await call.message.delete()
                return

            not_subscribed = []

            for channel in channels:
                channel_id = channel[1]
                channel_name = channel[2]
                channel_url = channel[3]

                try:
                    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                    if member.status in ['left', 'kicked']:
                        not_subscribed.append({
                            'name': channel_name,
                            'url': channel_url
                        })
                except Exception as e:
                    print(f"❌ Kanal tekshirishda xato: {e}")

            if not_subscribed:
                # Hali obuna bo'lmagan
                await call.answer(
                    "❌ Iltimos, barcha kanallarga obuna bo'ling!",
                    show_alert=True
                )
            else:
                # Obuna tasdiqlandi
                await call.answer(
                    "✅ Obuna tasdiqlandi!\n\nEndi botdan foydalanishingiz mumkin!",
                    show_alert=True
                )
                await call.message.delete()
        else:
            # Boshqa callbacklar uchun ham tekshirish
            user_id = call.from_user.id

            if str(user_id) in ADMINS:
                return

            db = Database()
            channels = db.get_all_channels()

            if not channels:
                return

            not_subscribed = []

            for channel in channels:
                channel_id = channel[1]
                channel_name = channel[2]
                channel_url = channel[3]

                try:
                    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                    if member.status in ['left', 'kicked']:
                        not_subscribed.append({
                            'name': channel_name,
                            'url': channel_url
                        })
                except Exception as e:
                    print(f"❌ Kanal tekshirishda xato: {e}")

            if not_subscribed:
                text = (
                    "❌ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart!</b>\n\n"
                    "📢 <b>Majburiy kanallar:</b>\n"
                )

                for idx, channel in enumerate(not_subscribed, 1):
                    text += f"{idx}. {channel['name']}\n"

                text += "\n👇 Obuna bo'ling va \"✅ Obunani tekshirish\" tugmasini bosing."

                await call.message.answer(
                    text,
                    reply_markup=check_subscription_keyboard(not_subscribed)
                )
                await call.answer(
                    "❌ Avval kanallarga obuna bo'ling!",
                    show_alert=True
                )

                raise CancelHandler()