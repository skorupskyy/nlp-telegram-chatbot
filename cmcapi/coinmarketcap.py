import os
import json
import requests
from requests.exceptions import HTTPError

from app.settings import (
    X_CMC_PRO_API_HEADERS,
    X_CMC_PRO_API_QUOTES_LATEST_URL,
    X_CMC_PRO_API_LISTINGS_LATEST_URL
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


def make_quotes_url(names, convert):
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


def make_listings_url(limit, convert, sort=None, sort_dir=None):
    full_url = X_CMC_PRO_API_LISTINGS_LATEST_URL

    full_url += '&limit={}&convert={}&'.format(limit, convert)
    if sort:
        full_url += 'sort={}&'.format(sort)

    if sort_dir:
        full_url += 'sort_dir={}&'.format(sort_dir)
    # full_url += 'sort_dir=asc&'

    full_url = full_url[:-1]
    return full_url


# names: list of crypto currency slugs or symbols (list of strings)
# convert: symbol of the crypto currency or fiat currency we want to convert to (string)
# usage:
# 	get_price(['BTC', 'ETH'], 'UAH')
# 	get_price(['bitcoin', 'ethereum'])
# returns list of dicts
def get_prices(names, convert='USD'):
    data = req(make_quotes_url(names, convert))

    def get_info(_x):
        currency = data['data'][_x]
        return {
            'from_name': currency['name'],
            'from_symbol': currency['symbol'],
            'rank': currency['cmc_rank'],
            'to_symbol': convert,
            'price': currency['quote'][convert]['price'],
            'change_per_1h': currency['quote'][convert]['percent_change_1h'],
            'change_per_24h': currency['quote'][convert]['percent_change_24h'],
            'change_per_7d': currency['quote'][convert]['percent_change_7d'],
            'market_capacity': int(currency['quote'][convert]['market_cap'])
        }

    return sorted(list(map(get_info, data['data'])), key=lambda x: x['rank'])


def get_listing(limit, convert="USD", sort=None, sort_dir=None):
    currencies = []
    full_url = make_listings_url(limit, convert, sort, sort_dir)
    data = req(full_url)

    count = 0
    for x in data['data']:
        currencies.append(data['data'][count]['name'])
        count += 1
    return currencies


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


def load_entities():
    currencies_path = '{}/entities.json'.format(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.exists(currencies_path)
    with open(currencies_path, 'r') as f:
        return json.load(f)


# Updates "./currency.json" file from listing api.
# overridden in entity_maker.py in update_currencies_json()
def update_currency_list():
    limit = 1000
    url = make_listings_url(limit, "USD")
    data = requests.get(
        url,
        headers=X_CMC_PRO_API_HEADERS
    ).json()['data']
    result = {'ripple': 'XRP'}
    for curr in data:
        result[curr['name'].lower()] = curr['symbol']
        result[curr['symbol'].lower()] = curr['symbol']
    with open('./currencies.json', 'w') as fp:
        json.dump(result, fp, indent=2)


# TODO: temporary driver program.
if __name__ == '__main__':
    # update_currency_list()
    # for i in get_prices(['BTC', 'ETH'], 'UAH'):
    # 	for y in i:
    # 		print('{}: {}'.format(y, i[y]))
    # 	?	print()
    print(get_listing(10, "UAH", "price", "desc"))
