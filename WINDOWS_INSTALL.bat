@echo off
chcp 65001 > nul
echo ================================
echo  Rektor Feedback Bot O'rnatish
echo ================================
echo.

echo [1/5] Virtual muhit yaratilmoqda...
python -m venv venv
if errorlevel 1 (
    echo ❌ Xato: Python o'rnatilmagan!
    echo Python 3.7+ ni https://python.org dan yuklab oling
    pause
    exit
)

echo [2/5] Virtual muhit faollashtirilmoqda...
call venv\Scripts\activate.bat

echo [3/5] Pip yangilanmoqda...
python -m pip install --upgrade pip --quiet

echo [4/5] Kutubxonalar o'rnatilmoqda...
pip install -r requirements.txt --quiet

echo [5/5] Tekshirish...
if exist ".env" (
    echo ✅ .env fayl topildi
) else (
    echo ⚠️  .env fayl yo'q! Iltimos yarating va sozlang
)

echo.
echo ================================
echo ✅ O'rnatish tugadi!
echo ================================
echo.
echo Keyingi qadamlar:
echo 1. .env faylni oching va sozlang
echo 2. start_bot.bat ni ishga tushiring
echo.
pause
