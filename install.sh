#!/bin/bash

echo "================================"
echo " Rektor Feedback Bot O'rnatish"
echo "================================"
echo ""

echo "[1/5] Virtual muhit yaratilmoqda..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Xato: Python3 o'rnatilmagan!"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv"
    exit 1
fi

echo "[2/5] Virtual muhit faollashtirilmoqda..."
source venv/bin/activate

echo "[3/5] Pip yangilanmoqda..."
pip install --upgrade pip --quiet

echo "[4/5] Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt --quiet

echo "[5/5] Tekshirish..."
if [ -f ".env" ]; then
    echo "✅ .env fayl topildi"
else
    echo "⚠️  .env fayl yo'q! Iltimos yarating va sozlang"
fi

echo ""
echo "================================"
echo "✅ O'rnatish tugadi!"
echo "================================"
echo ""
echo "Keyingi qadamlar:"
echo "1. .env faylni oching va sozlang"
echo "2. ./start_bot.sh ni ishga tushiring"
echo ""
