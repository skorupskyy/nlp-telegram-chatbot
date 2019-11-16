from datetime import datetime

from bot import messages as msg
from bot.logging import logger as default_logger

from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, MessageHandler


class CurrencyInfoBot:

	def __init__(self, token, logger=None):
		# If passed logger is None, setup default logger.
		if not logger:
			logger = default_logger
		self._logger = logger

		# Available bot handlers, order is required!
		handlers = [
			# Handlers on different commands
			CommandHandler('start', self.start_command),
			CommandHandler('stop', self.stop_command),

			# Send a message when the command /help is issued.
			CommandHandler('help', self.reply(msg.HELP)),

			# Handlers on message
			MessageHandler(Filters.text, self.text_message),
			MessageHandler(Filters.voice, self.voice_message),

			# Handle all other message types.
			MessageHandler(Filters.all, self.reply(msg.INVALID))
		]

		# Create the Updater and pass it bot's token.
		# Make sure to set use_context=True to use the new context based callbacks.
		self._updater = Updater(token, use_context=True)

		# Get the dispatcher to register handlers.
		dp = self._updater.dispatcher

		# Setup handlers.
		for handler in handlers:
			dp.add_handler(handler)

		# log all errors.
		dp.add_error_handler(self._log_error)

	def start(self):
		self._logger.info('Bot started at {}'.format(datetime.now()))

		# Start the bot.
		self._updater.start_polling()

		# Block until the user presses Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		self._updater.idle()

	@staticmethod
	def reply(message):
		"""Wrapper to send a text message."""
		def inner(update, context):
			return update.message.reply_text(message)
		return inner

	@staticmethod
	def start_command(update, context):
		"""Send a message when the command /start is issued."""
		update.message.reply_text(msg.START)

	@staticmethod
	def stop_command(update, context):
		"""Send a message when the command /stop is issued."""
		update.message.reply_text(msg.STOP)

	@staticmethod
	def text_message(update, context):
		"""Handle the text message."""
		update.message.reply_text(update.message.text)

	@staticmethod
	def voice_message(update, context):
		"""Handle an voice message."""
		update.message.reply_text('Processing voice message...')

	@staticmethod
	def other_message(update, context):
		"""Handle all other message types."""
		if update.message:
			update.message.reply_text(msg.INVALID)

	def _log_error(self, update, context):
		"""Log Errors caused by Updates."""
		self._logger.warning('Update "%s" caused error "%s"', update, context.error)
