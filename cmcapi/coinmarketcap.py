import time, requests, json
import datetime as data
from cmcapi.settings import headers, latest_quotes_url

url = latest_quotes_url
headers = headers

def check_is_symbol(name):
    is_symbol = False
    if name.isupper():
        is_symbol = True
    return is_symbol

def req(url):
    request = requests.get(url, headers=headers)
    data = request.json()
    if request.status_code == 200:
        return data
    else:
        # todo: handle errors
        print(data['status']['error_message'])

def form_url(names, convert):
    fullurl = url
    count_of_symbols = 0
    for x in names:
        if check_is_symbol(x) == True:
            count_of_symbols += 1

    if count_of_symbols == len(names):
        fullurl += "symbol="
    else:
        fullurl += "slug="

    for x in names:
        fullurl += str(x) + ","
    fullurl = fullurl[:-1]

    fullurl += "&convert=" + str(convert)

    return fullurl


def get_price(names, convert="USD"):
    '''
    names: list of cryptocurrency slugs or symbols (list of strings)
    convert: symbol of the cryptocurrency or fiat currency we want to convert to (string)
    usage:
        get_price(["BTC", "ETH"], "UAH")
        get_price(["bitcoin", "ethereum"])
    returns list of dicts
    '''
    currencies = {}
    result = []
    full_url = form_url(names, convert)
    data = req(full_url)

    for x in data['data']:
        currencies[x] = data['data'][x]['name']

    for x in currencies:
        result.append({
            "Name" : currencies[x],
            "Symbol" : data['data'][x]['symbol'],
            "Rank" : data['data'][x]['cmc_rank'],
            "Convert currency" : convert,
            "Current price" : data['data'][x]['quote'][convert]['price'],
            "Percent change per 1h" : data['data'][x]['quote'][convert]['percent_change_1h'],
            "Percent change per 24h" : data['data'][x]['quote'][convert]['percent_change_24h'],
            "Percent change per 7d" : data['data'][x]['quote'][convert]['percent_change_7d'],
            "Market capacity" : data['data'][x]['quote'][convert]['market_cap']
        })
    return result

if __name__ == "__main__":
    for x in get_price(["BTC", "ETH"], "UAH"):
        for y in x:
            print("{} : {}".format(y, x[y]))
    print()
