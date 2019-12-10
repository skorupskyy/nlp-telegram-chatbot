import os
from threading import RLock

from pyswip import Prolog
from pyswip.prolog import PrologError

from app.settings import BASE_DIR

DEFAULT_RULES = [
	'get_crypto_currencies(User_id, X) :- crypto_currency(X), exchange(User_id, X).',
	'get_fiat_currencies(User_id, X) :- fiat_currency(X), exchange(User_id, X).',
	'exists_currency(Currency_name) :- fiat_currency(Currency_name); crypto_currency(Currency_name).',
	'% section.facts'
]


class PrologKb:
	
	def __init__(self, file_path):
		assert file_path is not None
		self._file_path = file_path.replace('\\', '/')
		
		self._kb_file = open(self._file_path, 'a+')
		self._prepare_file()
		self._guard = RLock()
		self._kb = Prolog()
		self._kb.consult(self._file_path)

	def _file_is_empty(self):
		return os.stat(self._file_path).st_size == 0

	def _clear_file(self):
		self._kb_file.close()
		self._kb_file = open(self._file_path, 'w').close()
		self._kb_file = open(self._file_path, 'a+')

	def __del__(self):
		self._kb_file.close()

	def _prepare_file(self):
		if self._file_is_empty():
			text_to_file = '\n'.join(DEFAULT_RULES)+'\n'
			self._kb_file.write(text_to_file)

	def _call(self, query):
		try:
			return list(self._kb.query(query))
		except PrologError:
			return None

	@staticmethod
	def _norm_currency(currency_name):
		return currency_name.strip().lower().replace(' ', '_')

	@staticmethod
	def _norm_user_id(user_id):
		return '"{}"'.format(user_id)

	# Checks whether fact exchange(user_id, currency_name) exists in kb.
	def _exists_exchange(self, user_id, currency_name):
		result = self._call('exchange({}, {})'.format(
			self._norm_user_id(user_id), self._norm_currency(currency_name)
		))
		return len(result) != 0 if result else False

	# Checks whether rule fiat_currency(currency_name)
	#   exists or rule crypto_currency(currency_name).
	def _exists_currency(self, currency_name):
		result = self._call('exists_currency({})'.format(
			self._norm_currency(currency_name)
		))
		return len(result) != 0 if result else False
	
	# Writes data to self._kb_file.
	def _write(self, data):
		if len(data) > 0:
			self._guard.acquire()
		
			self._kb_file.write(data)
			self._kb_file.flush()
			os.fsync(self._kb_file.fileno())
			
			self._kb.consult(self._file_path)
			
			self._guard.release()

	# Returns list of facts exchange relative to user_id.
	def get_exchanges(self, user_id):
		result = self._call('exchange({}, Y)'.format(
			self._norm_user_id(user_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))

	# Returns list of crypto currencies exchanged by a user_id.
	def get_crypto_currencies(self, user_id):
		result = self._call('get_crypto_currencies({}, Y)'.format(
			self._norm_user_id(user_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))
	
	# Returns list of fiat currencies exchanged by a user_id.
	def get_fiat_currencies(self, used_id):	
		result = self._call('get_fiat_currencies({}, Y)'.format(
			self._norm_user_id(used_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))

	# Add fact exchange(user_id, currency) to kb.
	def add_exchange(self, user_id, currency, is_fiat=True):
		if not self._exists_exchange(user_id, currency):
			self._write('exchange({}, {}).\n'.format(
				self._norm_user_id(user_id),
				self._norm_currency(currency)
			))
			if not self._exists_currency(currency):
				if is_fiat:
					self._write('fiat_currency({}).\n'.format(self._norm_currency(currency)))
				else:
					self._write('crypto_currency({}).\n'.format(self._norm_currency(currency)))

	# Add list of facts exchange(user_id, currency) to kb.
	def add_exchanges(self, user_id, currencies):
		facts = []
		norm_user = self._norm_user_id(user_id)
		for currency, is_fiat in currencies:
			if not self._exists_exchange(user_id, currency):
				facts.append('exchange({}, {}).'.format(norm_user, self._norm_currency(currency)))
				if not self._exists_currency(currency):
					if is_fiat:
						facts.append('fiat_currency({}).'.format(self._norm_currency(currency)))
					else:
						facts.append('crypto_currency({}).'.format(self._norm_currency(currency)))
		if not (len(facts) == 0):
			text_to_file = '\n'.join(facts)+'\n'
			self._write(text_to_file)


# Simple driver program.
# TODO: will be removed in future.
def main():
	kb = PrologKb('{}/kb.pro'.format(BASE_DIR))
	
	kb.add_exchange(5, 'euro')
	li = [('dollar', True), ('ether', False)]
	kb.add_exchanges(74, li)

	print(kb.get_crypto_currencies(74))	
	print(kb.get_fiat_currencies(74))
	

if __name__ == '__main__':
	main()
