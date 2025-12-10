"""
Telegram Bot Davomat Tizimi Moduli
"""

from .handlers import register_all_attendance_handlers, handle_attendance_deeplink
from .utils import AttendanceDB, generate_attendance_qr
from .keyboards import user_main_menu, admin_attendance_menu
from .config import BOT_TOKEN, BOT_USERNAME, ADMINS, is_admin

__version__ = "1.0.0"
__all__ = [
    'register_all_attendance_handlers',
    'handle_attendance_deeplink',
    'AttendanceDB',
    'generate_attendance_qr',
    'user_main_menu',
    'admin_attendance_menu',
    'BOT_TOKEN',
    'BOT_USERNAME',
    'ADMINS',
    'is_admin'
]
