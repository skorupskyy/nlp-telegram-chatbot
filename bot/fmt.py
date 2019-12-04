
_title = '{from_name} ({from_symbol})'

_ext_title = _title + ' -> {to_symbol}'

_price = '1 {from_symbol} = {price} {to_symbol}'

_rank = 'Rank: {rank}'

_currency_change = """Change:
  1 hour:   {change_per_1h}
  24 hours: {change_per_24h}
  7 days:   {change_per_7d}"""

_market_capacity = 'Market capacity: {market_capacity}'

_general = '{}\n{}\n{}\n{}\n{}'.format(_ext_title, _price, _rank, _currency_change, _market_capacity)


def format_currencies(template, currencies, keys):
	formatted = []
	for curr in currencies:
		formatted.append(template.format(**{key: curr[key] for key in keys}))
	return '\n\n'.join(formatted)


def make_general(currencies):
	return format_currencies(_general, currencies, [
		'from_name', 'from_symbol', 'to_symbol', 'price',
		'rank', 'change_per_1h', 'change_per_24h',
		'change_per_7d', 'market_capacity'
	])


def make_price(currencies):
	return format_currencies('{}\n{}'.format(_ext_title, _price), currencies, [
		'from_name', 'from_symbol', 'to_symbol', 'price'
	])


def make_change(currencies):
	return format_currencies('{}\n{}'.format(_title, _currency_change), currencies, [
		'from_name', 'from_symbol', 'change_per_1h',
		'change_per_24h', 'change_per_7d'
	])
