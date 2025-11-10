# 🚀 Rektor Feedback Bot - O'rnatish Qo'llanmasi

## 1️⃣ Telegram Bot yaratish

### Bot yaratish:
1. Telegram'da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot uchun **nom** kiriting (masalan: `Universitet Feedback Bot`)
4. Bot uchun **username** kiriting (masalan: `universitet_feedback_bot`)
5. BotFather sizga **token** beradi, uni saqlab qo'ying!

Misol:
```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

## 2️⃣ Admin ID topish

1. Telegram'da **@userinfobot** ga yozing
2. `/start` buyrug'ini yuboring
3. Bot sizga **ID raqamingizni** ko'rsatadi (masalan: `123456789`)
4. Bu raqamni yozib qo'ying!

## 3️⃣ Botni serverga o'rnatish

### Python o'rnatish (agar yo'q bo'lsa):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y
```

### Botni yuklab olish:
```bash
# ZIP faylni serverga yuklang
unzip rector_feedback_bot.zip
cd rector_feedback_bot
```

### Virtual muhit yaratish:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Kutubxonalarni o'rnatish:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Agar xato chiqsa:**
```bash
pip uninstall environs marshmallow -y
pip install -r requirements.txt
```

## 4️⃣ Sozlamalarni kiritish

### .env faylni tahrirlash:
```bash
nano .env
```

Quyidagi qiymatlarni o'zgartiring:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
ADMINS=123456789
IP=localhost
```

- **BOT_TOKEN** - BotFather'dan olgan token
- **ADMINS** - Sizning ID raqamingiz (bir nechta bo'lsa vergul bilan: `123456789,987654321`)

**Saqlash:** `Ctrl + O`, `Enter`, `Ctrl + X`

## 5️⃣ Botni ishga tushirish

### Oddiy ishga tushirish:
```bash
python3 app.py
```

### Screen bilan ishga tushirish (yopilmaydi):
```bash
screen -S rectorbot
python3 app.py

# Chiqish: Ctrl + A, keyin D
# Qaytish: screen -r rectorbot
```

### Systemd service yaratish (avtomatik ishga tushirish):
```bash
sudo nano /etc/systemd/system/rectorbot.service
```

Quyidagini yozing:
```ini
[Unit]
Description=Rector Feedback Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rector_feedback_bot
Environment="PATH=/home/ubuntu/rector_feedback_bot/venv/bin"
ExecStart=/home/ubuntu/rector_feedback_bot/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Saqlang va yoping. Keyin:
```bash
sudo systemctl daemon-reload
sudo systemctl start rectorbot
sudo systemctl enable rectorbot
sudo systemctl status rectorbot
```

## 6️⃣ Majburiy obuna sozlash (ixtiyoriy)

### Kanal yaratish:
1. Telegram'da yangi **kanal** yarating
2. Kanal sozlamalaridan **public** qiling
3. Kanal username o'rnating (masalan: `universitet_news`)

### Botni kanalga admin qilish:
1. Kanalga kiring
2. **Kanalga admin qo'shish** → Botingizni qidiring va admin qiling
3. "Xabar yuborish" va "Foydalanuvchilarni boshqarish" huquqlarini bering

### Kanalni botga qo'shish:
1. Botga `/start` yuboring
2. **"📺 Kanallar"** tugmasini bosing
3. **"➕ Kanal qo'shish"** ni tanlang
4. Kanal ID sini yuboring: `@universitet_news`
5. Kanal URL sini yuboring: `https://t.me/universitet_news`

## 7️⃣ Tekshirish

### Bot ishlayotganini tekshirish:
1. Telegram'da botingizni oching
2. `/start` yuboring
3. Agar bot javob bersa - hammasi joyida! ✅

### Admin panel tekshirish:
1. Botga `/start` yuboring
2. Admin tugmalari ko'rinishi kerak:
   - 📊 Statistika
   - 📢 Reklama yuborish
   - 📺 Kanallar

## 🆘 Muammolar va Yechimlar

### Bot ishlamayapti:
```bash
# Loglarni ko'rish
journalctl -u rectorbot -f
```

### "Bot token is invalid" xatosi:
- .env fayldagi BOT_TOKEN ni tekshiring
- BotFather'dan yangi token oling

### "Admin ID" ishlamayapti:
- @userinfobot'dan to'g'ri ID ni oling
- .env fayldagi ADMINS qismiga to'g'ri kiriting

### Kanal qo'shib bo'lmayapti:
- Botni kanalga admin qilganingizni tekshiring
- Kanal public ekanligini tekshiring

## 📞 Yordam

Qo'shimcha savol yoki muammolar bo'lsa:
- README.md faylni o'qing
- Barcha sozlamalarni qayta tekshiring
- Python va kutubxonalar versiyasini tekshiring

---

**Omad! Bot muvaffaqiyatli ishlashini tilaymiz! 🎉**
