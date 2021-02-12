import os
from threading import RLock
from datetime import datetime

import pyswip
import ctypes
from pyswip.prolog import PrologError

from app.settings import BASE_DIR

DEFAULT_RULES = [
	'get_crypto_currencies(User_id, X, Tstamp) :- crypto_currency(X), exchange(User_id, X, Tstamp).',
	'get_fiat_currencies(User_id, X, Tstamp) :- fiat_currency(X), exchange(User_id, X, Tstamp).',
	'exists_currency(Currency_name) :- fiat_currency(Currency_name); crypto_currency(Currency_name).',
	'% section.facts'
]

EXCHANGE_FACT = 'exchange({}, {}, {})'

TIMESTAMP_FORMAT = '%d-%b-%Y (%H:%M:%S.%f)'


class PrologMT(pyswip.Prolog):
	"""Multi-threaded (one-to-one) pyswip.Prolog ad-hoc reimpl"""
	_swipl = pyswip.core._lib

	PL_thread_self = _swipl.PL_thread_self
	PL_thread_self.restype = ctypes.c_int

	PL_thread_attach_engine = _swipl.PL_thread_attach_engine
	PL_thread_attach_engine.argtypes = [ctypes.c_void_p]
	PL_thread_attach_engine.restype = ctypes.c_int

	@classmethod
	def _init_prolog_thread(cls):
		pengine_id = cls.PL_thread_self()
		if pengine_id == -1:
			pengine_id = cls.PL_thread_attach_engine(None)
			# Attach pengine to thread pengine_id
		if pengine_id == -1:
			raise pyswip.prolog.PrologError("Unable to attach new Prolog engine to the thread")

	class _QueryWrapper(pyswip.Prolog._QueryWrapper):
		def __call__(self, *args, **kwargs):
			PrologMT._init_prolog_thread()
			return super().__call__(*args, **kwargs)


class PrologKb:
	def __init__(self, file_path='{}/kb.pro'.format(BASE_DIR)):
		assert file_path is not None
		self._file_path = file_path.replace('\\', '/')
		
		self._kb_file = open(self._file_path, 'a+')
		self._prepare_file()
		self._guard = RLock()
		self._kb = PrologMT()
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
			li = list(self._kb.query(query))
			return li
		except PrologError:
			return None

	@staticmethod
	def _norm_currency(currency_name):
		return currency_name.strip().lower().replace(' ', '_')

	@staticmethod
	def _norm_user_id(user_id):
		return '{}'.format(user_id)
	
	@staticmethod
	def _get_timestamp():
		return '"{}"'.format(datetime.now().strftime(TIMESTAMP_FORMAT))
	
	@staticmethod
	def _from_timestamp(timestamp):
		return datetime.strptime(timestamp, TIMESTAMP_FORMAT)

	# Checks whether fact exchange(user_id, currency_name) exists in kb.
	def _exists_exchange(self, user_id, currency_name):
		result = self._call(EXCHANGE_FACT.format(
			self._norm_user_id(user_id), self._norm_currency(currency_name), '_'
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
		
	# Returns list of currencies exchanged by a user_id
	#   according to rule template.
	def _get_list_of_exchanges(self, rule_template, user_id):
		result = self._call(
			rule_template.format(self._norm_user_id(user_id))
		)
		if not result:
			return []
		return list(set(map(lambda x: x['Y'], sorted(result, key=lambda a: self._from_timestamp(a['Z'].decode())))))

	# Returns list of cryptocurrencies exchanged by a user_id.
	def get_crypto_currencies(self, user_id):
		return self._get_list_of_exchanges('get_crypto_currencies({}, Y, Z)', user_id)
	
	# Returns list of fiat currencies exchanged by a user_id.
	def get_fiat_currencies(self, user_id):
		return self._get_list_of_exchanges('get_fiat_currencies({}, Y, Z)', user_id)

	# Returns list of facts exchange relative to user_id.
	def get_exchanges(self, user_id):
		return self._get_list_of_exchanges('exchange({}, Y, Z)', user_id)

	# Add fact exchange(user_id, currency) to kb.
	def add_exchange(self, user_id, currency, is_fiat=True):
		if len(currency) > 0:
			# if not self._exists_exchange(user_id, currency):
			self._write('{}.\n'.format(
				EXCHANGE_FACT.format(
					self._norm_user_id(user_id),
					self._norm_currency(currency),
					self._get_timestamp()
				)
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
				facts.append('{}.'.format(
					EXCHANGE_FACT.format(
						norm_user,
						self._norm_currency(currency),
						self._get_timestamp()
					))
				)
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
	kb = PrologKb()
	
	kb.add_exchange(366889066, 'EUR', True)
	li = [('dollar', True), ('ether', False)]
	kb.add_exchanges(74, li)

	print(kb.get_crypto_currencies(74))	
	print(kb.get_fiat_currencies(74))
	

if __name__ == '__main__':
	main()
