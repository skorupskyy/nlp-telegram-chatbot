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


def form_url(names, convert):
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


def get_price(names, convert='USD'):
	"""
	names: list of crypto currency slugs or symbols (list of strings)
	convert: symbol of the crypto currency or fiat currency we want to convert to (string)
	usage:
		get_price(["BTC", "ETH"], "UAH")
		get_price(["bitcoin", "ethereum"])
	returns list of dicts
	"""
	currencies = {}
	data = req(form_url(names, convert))
	
	for x in data['data']:
		currencies[x] = data['data'][x]['name']

	def get_info(_x):
		return {
			'name': currencies[_x],
			'symbol': data['data'][_x]['symbol'],
			'rank': data['data'][_x]['cmc_rank'],
			'convert_currency': convert,
			'current_price': data['data'][_x]['quote'][convert]['price'],
			'percent_change_per_1h': data['data'][_x]['quote'][convert]['percent_change_1h'],
			'percent_change_per_24h': data['data'][_x]['quote'][convert]['percent_change_24h'],
			'percent_change_per_7d': data['data'][_x]['quote'][convert]['percent_change_7d'],
			'market_capacity': data['data'][_x]['quote'][convert]['market_cap']
		}
	
	return list(map(get_info, currencies))


# TODO: temporary driver program.
if __name__ == '__main__':
	for i in get_price(['BTC', 'ETH'], 'UAH'):
		for y in i:
			print('{}: {}'.format(y, i[y]))
	print()
