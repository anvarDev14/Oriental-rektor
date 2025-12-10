# 📋 Telegram Bot Davomat Tizimi

## O'rnatish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. .env faylni sozlash
`.env.example` dan `.env` yarating:
```bash
cp .env.example .env
```

Keyin `.env` faylni tahrirlang:
```env
BOT_TOKEN=1234567890:ABCDefghIJKLmnopQRSTuvwxYZ
BOT_USERNAME=sam_oriental_support_bot
ADMINS=123456789,987654321
DATABASE_PATH=data/main.db
```

### 3. Botga qo'shish

`app.py` yoki asosiy faylda:
```python
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from attendance_module import (
    register_all_attendance_handlers,
    handle_attendance_deeplink,
    BOT_TOKEN, AttendanceDB
)
from attendance_module.keyboards import user_main_menu

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Start handler
@dp.message_handler(commands=['start'])
async def cmd_start(message):
    args = message.get_args()
    
    # QR dan kelgan bo'lsa
    if args and args.startswith("att_"):
        await handle_attendance_deeplink(message)
        return
    
    # Oddiy start
    db = AttendanceDB()
    is_registered = db.is_student_registered(message.from_user.id)
    
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!",
        reply_markup=user_main_menu(is_registered=is_registered)
    )

# Davomat handlerlarini qo'shish
register_all_attendance_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp)
```

## Qanday ishlaydi

```
1️⃣ Talaba "📋 Ro'yxatdan o'tish" bosadi
   └── Ism, ID, Yo'nalish, Guruh kiritadi

2️⃣ Admin "📋 Davomat" → "🆕 Yangi dars" bosadi
   └── Yo'nalish → Guruh → Fan → Davomiylik → QR oladi

3️⃣ QR kod proyektorda ko'rsatiladi
   └── Talabalar telefon kamerasi bilan skanerlaydi

4️⃣ Talaba QR skanerlaydi
   └── Bot ochiladi → Avtomatik davomat ✅

5️⃣ Admin "📊 Hisobot olish" bosadi
   └── Excel fayl yuklab oladi
```

## Fayl strukturasi

```
attendance_module/
├── .env.example          # Env namuna
├── config.py             # Konfiguratsiya
├── requirements.txt      # Kutubxonalar
├── __init__.py
├── handlers/
│   ├── registration.py   # Ro'yxatdan o'tish
│   ├── attendance.py     # QR davomat
│   └── admin_panel.py    # Admin boshqaruvi
├── keyboards/
│   └── attendance_kb.py  # Tugmalar
├── states/
│   └── attendance_states.py
└── utils/
    ├── attendance_db.py  # Database
    ├── qr_generator.py   # QR yaratish
    └── excel_export.py   # Excel hisobot
```

## Admin menusiga tugma qo'shish

Mavjud botingizda admin menusiga qo'shing:
```python
keyboard.add(KeyboardButton("📋 Davomat"))
```
