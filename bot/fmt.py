

_title = '{from_name}({from_symbol})'

_ext_title = _title + ' -> {to_symbol}'

_price = '1 {from_symbol} = {price} {to_symbol}'

_rank = 'Rank: {rank}'

_currency_change = """Change:
  1 hour: {change_per_1h}%
  24 hours: {change_per_24h}%
  7 days: {change_per_7d}%"""

_market_capacity = 'Market capacity: {capacity}'

_general = _ext_title + '\n' + _price + '\n' + _rank + '\n' + _currency_change + '\n' + _market_capacity


def make_general(currencies):
	formatted = []
	for curr in currencies:
		formatted.append(_general.format(
			from_name=curr['name'],
			from_symbol=curr['symbol'],
			to_symbol=curr['convert_currency'],
			price=round(curr['current_price'], 3),
			rank=curr['rank'],
			change_per_1h=curr['percent_change_per_1h'],
			change_per_24h=curr['percent_change_per_24h'],
			change_per_7d=curr['percent_change_per_7d'],
			capacity=curr['market_capacity'],
		))
	return '\n\n'.join(formatted)


def make_price(currencies):
	formatted = []
	template = _ext_title + '\n' + _price
	for curr in currencies:
		formatted.append(
			template.format(
				from_name=curr['name'],
				from_symbol=curr['symbol'],
				to_symbol=curr['convert_currency'],
				price=round(curr['current_price'], 3)
			)
		)
	return '\n\n'.join(formatted)
