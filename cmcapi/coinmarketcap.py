import requests
from cmcapi.settings import headers, latest_quotes_url


def check_is_symbol(name):
	return name.isupper()


def req(url):
	request = requests.get(url, headers=headers)
	data = request.json()
	if request.status_code == 200:
		return data
	else:
		# todo: handle errors
		print(data['status']['error_message'])


def form_url(names, convert):
	full_url = latest_quotes_url
	count_of_symbols = 0
	for x in names:
		if check_is_symbol(x):
			count_of_symbols += 1

	if count_of_symbols == len(names):
		full_url += 'symbol='
	else:
		full_url += 'slug='

	for x in names:
		full_url += str(x) + ","
	full_url = full_url[:-1]

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
	result = []
	full_url = form_url(names, convert)
	data = req(full_url)

	for x in data['data']:
		currencies[x] = data['data'][x]['name']

	for x in currencies:
		result.append({
			'name': currencies[x],
			'symbol': data['data'][x]['symbol'],
			'rank': data['data'][x]['cmc_rank'],
			'convert_currency': convert,
			'current_price': data['data'][x]['quote'][convert]['price'],
			'percent_change_per_1h': data['data'][x]['quote'][convert]['percent_change_1h'],
			'percent_change_per_24h': data['data'][x]['quote'][convert]['percent_change_24h'],
			'percent_change_per_7d': data['data'][x]['quote'][convert]['percent_change_7d'],
			'market_capacity': data['data'][x]['quote'][convert]['market_cap']
		})
	return result


# TODO: temporary driver program.
if __name__ == '__main__':
	for i in get_price(['BTC', 'ETH'], 'UAH'):
		for y in i:
			print('{} : {}'.format(y, i[y]))
	print()
