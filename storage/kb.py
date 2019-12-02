import os
import mmap
from threading import RLock

from pyswip import Prolog
from pyswip.prolog import PrologError

from app.settings import BASE_DIR


class PrologKb:
	
	def __init__(self, file_path):
		assert file_path is not None
		self._file_path = file_path
		
		self._kb_file = open(self._file_path, 'a+')
		self._prepare_file()
		
		self._guard = RLock()
		
		self._kb = Prolog()
		self._kb.consult(self._file_path)

	def __del__(self):
		self._kb_file.write('% section.facts.end\n')
		self._kb_file.close()

	def _prepare_file(self):
		if self._kb_file.tell() == 0:
			section_begin = '% section.facts.begin\n'
			self._kb_file.write(section_begin)
		else:
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

	def _exists(self, user_id, currency_name):
		result = self._call('currency({}, {})'.format(
			self._norm_user_id(user_id), self._norm_currency(currency_name)
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
		result = self._call('currency({}, Y)'.format(
			self._norm_user_id(user_id)
		))
		if not result:
			return []
		return list(map(lambda x: x['Y'], result))
	
	def add_currency(self, user_id, currency):
		if not self._exists(user_id, currency):
			self._write('currency({}, {}).\n'.format(
				self._norm_user_id(user_id),
				self._norm_currency(currency)
			))

	def add_currencies(self, user_id, currencies):
		facts = []
		norm_user = self._norm_user_id(user_id)
		for currency in currencies:
			if not self._exists(user_id, currency):
				facts.append('currency({}, {}).'.format(norm_user, self._norm_currency(currency)))
		self._write('\n'.join(facts))


# Simple driver program.
# TODO: will be removed in future.
if __name__ == '__main__':
	kb = PrologKb('{}/kb.pro'.format(BASE_DIR))
	print(kb.get_currencies(5))
	
	kb.add_currency(5, 'bitcoin')
	
	print(kb.get_currencies(12345))
