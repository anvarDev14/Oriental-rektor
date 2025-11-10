# 🔧 Muammolarni Hal Qilish

## ❌ AttributeError: module 'marshmallow' has no attribute '__version__'

Bu xato `environs` va `marshmallow` versiyalari o'rtasidagi muammo.

### ✅ Yechim 1 (Tavsiya etiladi):
```bash
# Virtual muhitni tozalash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Kutubxonalarni qayta o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

### ✅ Yechim 2:
```bash
pip uninstall environs marshmallow -y
pip install python-dotenv==1.0.0
pip install aiogram==2.25.1
```

### ✅ Yechim 3:
```bash
pip install --upgrade environs marshmallow
```

---

## ❌ ModuleNotFoundError: No module named 'aiogram'

### ✅ Yechim:
```bash
# Virtual muhit ichida ekanligingizni tekshiring
which python  # Linux/Mac
where python  # Windows

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

---

## ❌ aiogram.utils.exceptions.Unauthorized: Unauthorized

Bot token noto'g'ri yoki o'chirilgan.

### ✅ Yechim:
1. @BotFather dan yangi token oling
2. `.env` fayldagi `BOT_TOKEN` ni yangilang
3. Tokenni to'g'ri nusxalaganingizni tekshiring (probel yoki qo'shimcha belgi bo'lmasin)

---

## ❌ Bot javob bermayapti

### ✅ Yechim:
```bash
# 1. Bot ishlab turganini tekshiring
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows

# 2. Loglarni ko'ring
python3 app.py

# 3. Internet ulanishini tekshiring
ping google.com

# 4. Tokenni tekshiring
cat .env  # Linux/Mac
type .env  # Windows
```

---

## ❌ sqlite3.OperationalError: database is locked

### ✅ Yechim:
```bash
# Bot jarayonini to'xtatish
pkill -f app.py  # Linux/Mac

# Database faylni o'chirish (ma'lumotlar yo'qoladi!)
rm database.db

# Botni qayta ishga tushirish
python3 app.py
```

---

## ❌ Admin panel ko'rinmayapti

### ✅ Yechim:
1. `.env` fayldagi `ADMINS` ni tekshiring
2. Admin ID to'g'ri ekanligini tekshiring (@userinfobot)
3. Botni qayta ishga tushiring
4. `/start` buyrug'ini qayta yuboring

---

## ❌ Majburiy obuna ishlamayapti

### ✅ Yechim:
1. Botni kanalga admin qiling
2. Kanalga quyidagi huquqlarni bering:
   - "Xabar yuborish"
   - "Foydalanuvchilarni boshqarish"
3. Kanal public bo'lishi kerak
4. Kanal ID ni to'g'ri kiriting (`@username` yoki `-100...`)

---

## 📝 Windows uchun maxsus

### Virtual muhit yaratish:
```bash
python -m venv venv
venv\Scripts\activate
```

### Agar `activate` ishlamasa:
```bash
# PowerShell'da
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate

# CMD'da
venv\Scripts\activate.bat
```

---

## 🐧 Linux/Ubuntu uchun

### Python 3 o'rnatish:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### Screen bilan ishga tushirish:
```bash
screen -S rectorbot
python3 app.py

# Chiqish: Ctrl+A, D
# Qaytish: screen -r rectorbot
```

---

## 🍎 MacOS uchun

### Python o'rnatish:
```bash
brew install python3
```

### Virtual muhit:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 🔍 Loglarni tekshirish

### Konsolda:
```bash
python3 app.py
```

### Faylga yozish:
```bash
python3 app.py > bot.log 2>&1
tail -f bot.log
```

---

## 📞 Hali ham ishlamasa?

1. **requirements.txt** ni qayta tekshiring
2. **Python versiyasi** 3.7+ ekanligini tekshiring: `python3 --version`
3. **.env** fayldagi barcha qiymatlarni tekshiring
4. **Bot tokenni** @BotFather'dan qayta oling
5. **Virtual muhitni** qayta yarating

---

**Agar muammo hal bo'lmasa:**
- Xato xabarini to'liq nusxalang
- Python versiyangizni yozing
- Operatsion tizimingizni bildiring
