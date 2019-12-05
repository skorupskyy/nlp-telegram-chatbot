import os


# Common.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Telegram Bot API.
TELEGRAM_BOT_TOKEN = 'set in local settings'


# Coin Market Cap API.
X_CMC_PRO_API_KEY = 'set in local settings'

X_CMC_PRO_API_QUOTES_LATEST_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?'

X_CMC_PRO_API_LISTINGS_LATEST_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?'

try:
	from app.local_settings import *
except ImportError:
	pass


# Coin Market Cap API.
X_CMC_PRO_API_HEADERS = {
	'Accept': 'application/json',
	'Accept-Encoding': 'deflate, gzip',
	'X-CMC_PRO_API_KEY': X_CMC_PRO_API_KEY,
}
