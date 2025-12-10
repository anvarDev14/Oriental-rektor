from .registration import register_registration_handlers
from .attendance import register_attendance_handlers, handle_attendance_deeplink
from .admin_panel import register_admin_handlers


def register_all_attendance_handlers(dp, admin_filter=None):
    """Barcha davomat handlerlarini ro'yxatdan o'tkazish"""
    register_registration_handlers(dp)
    register_attendance_handlers(dp)
    register_admin_handlers(dp, admin_filter)
