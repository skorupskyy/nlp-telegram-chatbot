import os


# Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Telegram Bot API
TELEGRAM_BOT_TOKEN = 'set in local settings'

try:
	from app.local_settings import TELEGRAM_BOT_TOKEN
except ImportError:
	pass
