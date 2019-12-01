from bot import CurrencyInfoBot
from bot.settings import TOKEN


def main():
	bot = CurrencyInfoBot(TOKEN)
	bot.start()


if __name__ == '__main__':
	main()
