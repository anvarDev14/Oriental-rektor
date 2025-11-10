# 📝 Rektor Feedback Bot

Talabalarning fikr va takliflarini rektorga yetkazish uchun Telegram bot.

## 🎯 Asosiy funksiyalar

### Talabalar uchun:
- ✍️ Fikr va takliflarni yozish
- ✅ Xabarni tasdiqlash
- ✏️ Xabarni yangilash/o'zgartirish
- ❌ Xabarni bekor qilish
- 📸 Rasm, video, audio va boshqa formatlarni yuborish

### Admin (Rektor) uchun:
- 📊 **Statistika** - foydalanuvchilar soni va kanallar
- 📢 **Reklama yuborish** - barcha foydalanuvchilarga xabar yuborish
  - Oddiy xabar yoki Forward
  - Hozir yoki keyinroq yuborish (5m, 2h, 1d, 1w)
  - Har qanday kontent turi (matn, rasm, video, audio)
- 📺 **Kanallar** - majburiy obuna kanallari
  - Kanal qo'shish
  - Kanal o'chirish
  - Kanallar ro'yxati

### Xususiyatlar:
- 🔒 Majburiy obuna tizimi
- 💾 SQLite database
- 🎨 Chiroyli interfeys
- ⏱️ Rejalashtirilgan xabarlar
- 📝 Xabarni tasdiqlash tizimi

## 🚀 O'rnatish

### 1. Repozitoriyni clone qiling:
```bash
git clone <repository_url>
cd rector_feedback_bot
```

### 2. Virtual muhit yarating:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

### 4. .env faylni sozlang:
```
BOT_TOKEN=sizning_bot_tokeningiz
ADMINS=123456789,987654321
IP=localhost
```

**Bot token olish:**
1. @BotFather ga murojaat qiling
2. /newbot buyrug'ini yuboring
3. Bot nomi va username kiriting
4. Tokenni .env fayliga joylashtiring

**Admin ID topish:**
1. @userinfobot ga /start yuboring
2. O'z ID raqamingizni oling
3. ADMINS ga qo'shing (vergul bilan ajratilgan)

### 5. Botni ishga tushiring:
```bash
python app.py
```

## 📁 Struktura

```
rector_feedback_bot/
├── app.py                  # Asosiy fayl
├── loader.py               # Bot va dispatcher
├── requirements.txt        # Kutubxonalar
├── .env                    # Sozlamalar
├── database.db            # Database (avtomatik yaratiladi)
│
├── data/
│   ├── __init__.py
│   └── config.py          # Konfiguratsiya
│
├── handlers/
│   ├── users/             # Foydalanuvchi handlerlari
│   │   ├── start.py
│   │   └── send_message.py
│   └── admins/            # Admin handlerlari
│       ├── admin_panel.py
│       ├── statistics.py
│       ├── broadcast.py
│       └── channels.py
│
├── keyboards/
│   ├── default/           # Oddiy klaviaturalar
│   │   └── menu.py
│   └── inline/            # Inline klaviaturalar
│       └── admin_keyboard.py
│
├── middlewares/
│   ├── __init__.py
│   └── check_subscription.py
│
├── filters/
│   ├── __init__.py
│   └── is_admin.py
│
├── states/
│   ├── __init__.py
│   └── message_states.py
│
└── utils/
    ├── db_api/
    │   └── database.py    # Database moduli
    ├── notify_admins.py
    └── set_bot_commands.py
```

## 🎮 Foydalanish

### Talaba:
1. Botga /start yuboring
2. "✍️ Xabar yozish" tugmasini bosing
3. Fikringizni yozing
4. Xabarni tasdiqlang

### Admin:
1. Botga /start yuboring (admin sifatida)
2. Admin panel ochiladi:
   - 📊 Statistika - foydalanuvchilar sonini ko'rish
   - 📢 Reklama yuborish - xabar yuborish
   - 📺 Kanallar - majburiy obuna sozlash

## 🔧 Texnologiyalar

- **Python 3.8+**
- **aiogram 2.14+** - Telegram Bot API
- **SQLite3** - Database
- **environs** - Environment o'zgaruvchilar

## 📝 Eslatma

- Bot ishga tushganda `database.db` avtomatik yaratiladi
- Adminlar majburiy obunadan ozod
- Xabarlar format saqlanadi (matn, rasm, video)
- Reklama har qanday vaqtga rejalashtirilishi mumkin

## 🤝 Yordam

Savollar yoki muammolar bo'lsa:
1. README.md ni qaytadan o'qing
2. .env faylni tekshiring
3. Bot tokenni to'g'ri kiriting
4. Admin ID to'g'ri ekanligini tekshiring

## 📄 Litsenziya

MIT License - istalgan maqsadda foydalanish mumkin.

---

**Muallif:** Claude AI
**Versiya:** 1.0.0
**Sana:** 2025
