"""
Konfiguratsiya fayli
"""
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'sam_oriental_support_bot')

ADMINS = os.getenv('ADMINS', '').split(',')
ADMINS = [admin.strip() for admin in ADMINS if admin.strip()]

# Rektor ID - faqat shu odamga xabarlar boradi
RECTOR_ID = os.getenv('RECTOR_ID', '')

DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/main.db')
DEFAULT_SESSION_DURATION = int(os.getenv('DEFAULT_SESSION_DURATION', 90))


def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMINS


def is_rector(user_id: int) -> bool:
    return str(user_id) == RECTOR_ID