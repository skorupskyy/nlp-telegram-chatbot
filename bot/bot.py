from datetime import datetime

from bot import messages as msg
from bot import fmt
from cmcapi import load_currencies, get_prices
from app.logging import logger as default_logger

from requests.exceptions import HTTPError

from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, MessageHandler


class CurrencyInfoBot:

	def __init__(self, token, logger=None):
		# If passed logger is None, setup default logger.
		if not logger:
			logger = default_logger
		self._logger = logger

		# Create the Updater and pass it bot's token.
		# Make sure to set use_context=True to use the new context based callbacks.
		self._updater = Updater(token, use_context=True)

		# Get the dispatcher to register handlers.
		dp = self._updater.dispatcher

		# log all errors.
		dp.add_error_handler(self._log_error)

		self._init_handlers(dp)
		
		self._currencies = load_currencies()

	def start(self):
		self._logger.info('Bot started at {}'.format(datetime.now()))

		# Start the bot.
		self._updater.start_polling()

		# Block until the user presses Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		self._updater.idle()

	def _init_handlers(self, dispatcher):
		# Available bot handlers, order is required!
		handlers = [
			# Handlers on different commands
			CommandHandler('start', self._start_command),
			CommandHandler('stop', self._stop_command),
			
			# Send a message when the command /help is issued.
			CommandHandler('help', self._reply(msg.HELP)),
			
			# Handlers on message
			MessageHandler(Filters.text, self._text_message),
			MessageHandler(Filters.voice, self._voice_message),
			
			# Handle all other message types.
			MessageHandler(Filters.all, self._reply(msg.INVALID))
		]

		# Setup handlers.
		for handler in handlers:
			dispatcher.add_handler(handler)

	# Wrapper to send a text message.
	@staticmethod
	def _reply(message):
		def inner(update, context):
			return update.message.reply_text(message)
		return inner

	# Sends a message when the command /start is issued.
	@staticmethod
	def _start_command(update, context):
		update.message.reply_text(msg.START)

	# Sends a message when the command /stop is issued.
	@staticmethod
	def _stop_command(update, context):
		update.message.reply_text(msg.STOP)

	# Handles the text message.
	def _text_message(self, update, context):
		input_text = update.message.text
		
		# TODO: extract crypto-currencies and convert currency using DialogFlow agent!
		currencies = list(map(lambda curr: curr.strip().lower(), input_text.split(',')))
		from_currs = self._normalize_currencies(currencies[:-1])
		to_curr = currencies[-1].upper()
		# TODO:----------------------------------------------------------------------^
		
		try:
			prices = get_prices(from_currs, to_curr)
			response_text = fmt.make_general(prices)
		except HTTPError as exc:
			self._logger.warning('Unable to receive prices: {}', exc)
			response_text = 'Service is currently unavailable...\nPlease, try again later...'
			
		update.message.reply_text(response_text)

	# Handles a voice message.
	@staticmethod
	def _voice_message(update, context):
		# TODO
		update.message.reply_text('Sorry...\nVoice messages currently is not supported =(')

	# Logs errors caused by updates.
	def _log_error(self, update, context):
		self._logger.warning('Update "%s" caused error "%s"', update, context.error)
		update.message.reply_text('Oops, something went wrong...')
	
	# Normalizes inputted currencies, i.e. Bitcoin -> BTC, xrp -> XRP, etc.
	def _normalize_currencies(self, input_currencies):
		normalized = []
		for item in input_currencies:
			if item in self._currencies:
				normalized.append(self._currencies[item])
		return normalized
