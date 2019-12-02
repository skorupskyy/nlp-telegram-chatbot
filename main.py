from bot import CurrencyInfoBot
from app.settings import TELEGRAM_BOT_TOKEN


def main():
	bot = CurrencyInfoBot(TELEGRAM_BOT_TOKEN)
	bot.start()


if __name__ == '__main__':
	main()
