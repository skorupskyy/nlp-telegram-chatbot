TOKEN = 'set in local settings'

try:
	from bot.local_settings import TOKEN
except ImportError:
	pass
