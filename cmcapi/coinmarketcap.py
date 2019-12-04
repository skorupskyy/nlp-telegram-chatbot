import os
import json

import requests
from requests.exceptions import HTTPError

from app.settings import (
	X_CMC_PRO_API_HEADERS,
	X_CMC_PRO_API_QUOTES_LATEST_URL
)


def check_is_symbol(name):
	return name.isupper()


# Throws HTTPError when request's status code is not 200.
def req(url):
	request = requests.get(url, headers=X_CMC_PRO_API_HEADERS)
	data = request.json()
	if request.status_code == 200:
		return data
	raise HTTPError(str(data['status']['error_message']))


def make_url(names, convert):
	full_url = X_CMC_PRO_API_QUOTES_LATEST_URL
	count_of_symbols = 0
	for x in names:
		if check_is_symbol(x):
			count_of_symbols += 1

	if count_of_symbols == len(names):
		full_url += 'symbol='
	else:
		full_url += 'slug='

	full_url += ','.join(names)
	full_url += '&convert={}'.format(convert)

	return full_url


# names: list of crypto currency slugs or symbols (list of strings)
# convert: symbol of the crypto currency or fiat currency we want to convert to (string)
# usage:
# 	get_price(['BTC', 'ETH'], 'UAH')
# 	get_price(['bitcoin', 'ethereum'])
# returns list of dicts
def get_prices(names, convert='USD'):
	data = req(make_url(names, convert))
	
	def get_info(_x):
		currency = data['data'][_x]
		return {
			'name': currency['name'],
			'symbol': currency['symbol'],
			'rank': currency['cmc_rank'],
			'convert_currency': convert,
			'current_price': currency['quote'][convert]['price'],
			'percent_change_per_1h': currency['quote'][convert]['percent_change_1h'],
			'percent_change_per_24h': currency['quote'][convert]['percent_change_24h'],
			'percent_change_per_7d': currency['quote'][convert]['percent_change_7d'],
			'market_capacity': currency['quote'][convert]['market_cap']
		}
	
	return list(map(get_info, data['data']))


# Loads list of currencies for normalization.
#
# "currencies.json" example:
# {
#   "bitcoin": "BTC",
#   "btc": "BTC",
#   "ripple": "XRP",
#   "xrp": "XRP",
# }
def load_currencies():
	currencies_path = '{}/currencies.json'.format(os.path.dirname(os.path.abspath(__file__)))
	assert os.path.exists(currencies_path)
	with open(currencies_path, 'r') as f:
		return json.load(f)


# TODO: temporary driver program.
if __name__ == '__main__':
	from bot.util import format_general
	print(format_general(get_price(['BTC', 'ETH'], 'UAH')))
	# from pprint import pprint
	# pprint(load_currencies())
	# for i in get_price(['BTC', 'ETH'], 'UAH'):
	# 	for y in i:
	# 		print('{}: {}'.format(y, i[y]))
	# print()
