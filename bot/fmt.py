_title = '{from_name} ({from_symbol})'

_ext_title = _title + ' -> {to_symbol}'

_price = '1 {from_symbol} = {price} {to_symbol}'

_rank = 'Global rank: {rank}'

_currency_change = """Change:
	1 hour:   {change_per_1h} %
	24 hours: {change_per_24h} %
	7 days:   {change_per_7d} %"""

_market_capacity = 'Market capacity: {market_capacity} {to_symbol}'

_general = '{}\n{}\n{}\n{}\n{}'.format(_ext_title, _price, _rank, _currency_change, _market_capacity)


def format_currencies(template, currencies, keys):
	# TODO: add space every 3 symbols in market capacity
	formatted = []
	for curr in currencies:
		formatted.append(template.format(**{key: curr[key] for key in keys}))
	return '\n\n'.join(formatted)


def make_one_currency(curs):
	def make_general(currencies):
		return format_currencies(_general, currencies, [
			'from_name', 'from_symbol', 'to_symbol', 'price',
			'rank', 'change_per_1h', 'change_per_24h',
			'change_per_7d', 'market_capacity'
		])
	return make_general(curs)


def make_currencies_top(currencies, sort):
	result = 'Top {} crypto currencies{}'.format(len(currencies), ' by {}'.format(sort) if sort and sort != [] else '')
	for idx, cur in enumerate(currencies):
		result += '\n {}. {}'.format(idx + 1, cur)

	return result


def make_price(currencies):
	return format_currencies('{}\n{}'.format(_ext_title, _price), currencies, [
		'from_name', 'from_symbol', 'to_symbol', 'price'
	])


def make_change(currencies):
	return format_currencies('{}\n{}'.format(_title, _currency_change), currencies, [
		'from_name', 'from_symbol', 'change_per_1h',
		'change_per_24h', 'change_per_7d'
	])
