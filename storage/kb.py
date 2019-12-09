import os
import mmap
from threading import RLock

from pyswip import Prolog
from pyswip.prolog import PrologError

from app.settings import BASE_DIR


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
		return os.stat(self._file_path).st_size==0

	def _clear_file(self):
		self._kb_file.close()
		self._kb_file = open(self._file_path, 'w').close()
		self._kb_file = open(self._file_path, 'a+')
	def __del__(self):
		#self._kb_file.write('% section.facts.end\n')
		self._kb_file.close()

	def _prepare_file(self):
		if self._file_is_empty():
			section_begin = '% section.facts.begin\n'
			self._kb_file.write(section_begin)
		else:
			return
			f = mmap.mmap(
				fileno=self._kb_file.fileno(),
				length=0,
				access=mmap.ACCESS_READ
			)
			end_section = f.find(b'% section.facts.end')
			if end_section == -1:
				raise EOFError('knowledge base has invalid end of facts section')
			self._kb_file.seek(end_section)
			self._kb_file.truncate()

	def _call(self, query):
		try:
			return list(self._kb.query(query))
		except PrologError:
			return None

	def _norm_currency(self, currency_name):
		return currency_name.strip().lower().replace(' ', '_')

	def _norm_user_id(self, user_id):
		return '"{}"'.format(user_id)

	def _exists_exchange(self, user_id, currency_name):
		result = self._call('exchange({}, {})'.format(
			self._norm_user_id(user_id), self._norm_currency(currency_name)
		))
		return len(result) != 0 if result else False

	#check whether rule fiat_currency(currency_name) exists or rule crypto_currency(currency_name).
	def _exists_currency(self, currency_name):
		result = self._call('exists_currency({})'.format(
			self._norm_currency(currency_name)
		))
		return len(result) != 0 if result else False
	
	def _write(self, data):
		if len(data) > 0:
			self._guard.acquire()
		
			self._kb_file.write(data)
			self._kb_file.flush()
			os.fsync(self._kb_file.fileno())
			
			self._kb.consult(self._file_path)
			
			self._guard.release()

	def get_currencies(self, user_id):
		result = self._call('exchange({}, Y)'.format(
			self._norm_user_id(user_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))

	def get_crypto_currencies(self, used_id):
		result = self._call('get_crypto_currencies({}, Y)'.format(
			self._norm_user_id(used_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))
	
	def get_fiat_currencies(self, used_id):
		result = self._call('get_fiat_currencies({}, Y)'.format(
			self._norm_user_id(used_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))

	def add_currency(self, user_id, currency, is_fiat = True):
		if len(self.get_currencies(user_id)) == 0:
			self._write('exchange({}, {}).\n'.format(
				self._norm_user_id(user_id),
				self._norm_currency(currency)
			))
			if not self._exists_currency(currency):
				if is_fiat:
					self._write('fiat_currency({}).\n'.format(
						self._norm_currency(currency)
					))
				else:
					self._write('crypto_currency({}).\n'.format(
						self._norm_currency(currency)
					))

	def add_currencies(self, user_id, currencies):
		facts = []
		norm_user = self._norm_user_id(user_id)
		for currency, is_fiat in currencies:
			if len(self.get_currencies(user_id)) == 0:
				facts.append('exchange({}, {}).'.format(norm_user, self._norm_currency(currency)))
				if not self._exists_currency(currency):
					if is_fiat:
						facts.append('fiat_currency({}).'.format(self._norm_currency(currency)))
					else:
						facts.append('crypto_currency({}).'.format(self._norm_currency(currency)))
		if not (len(facts) == 0):
			text_to_file = '\n'.join(facts)+'\n'
			self._write(text_to_file)

def init():
    kb = PrologKb('{}\\kb.pro'.format(BASE_DIR))
    kb._clear_file()
    rules = [
        'get_crypto_currencies(User_id, X) :- crypto_currency(X), exchange(User_id, X).',
        'get_fiat_currencies(User_id, X) :- fiat_currency(X), exchange(User_id, X).',
        'exists_currency(Currency_name) :- fiat_currency(Currency_name); crypto_currency(Currency_name).',
        '% section.facts.begin'
		#,
        #'% section.facts.end'
    ]
    text_to_file = '\n'.join(rules)+'\n'
    kb._write(text_to_file)

    
# Simple driver program.
# TODO: will be removed in future.

def main():
	kb = PrologKb('{}\\kb.pro'.format(BASE_DIR))
	print(kb.get_currencies(5))
	
	kb.add_currency(5, 'euro')
	li = [('dollar',True), ('ether', False)]
	kb.add_currencies(74, li)

	print(kb.get_crypto_currencies(74))	
	print(kb.get_fiat_currencies(74))
	

if __name__ == '__main__':
	main()