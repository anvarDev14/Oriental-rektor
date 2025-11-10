@echo off
chcp 65001 > nul
echo ================================
echo  Rektor Feedback Bot
echo ================================
echo.
echo Bot ishga tushirilmoqda...
echo.

call venv\Scripts\activate.bat
python app.py

pause
