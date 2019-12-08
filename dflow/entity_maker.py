import requests
import json
from app.settings import DIALOGFLOW_DEV_TOKEN


def make_first_upper(word):
    return word[0].upper() + word[1:len(word)]


def make_all_lower(word):
    return word.lower()


def make_simple_entity(name, symbol):
    result = {}
    value = make_first_upper(name)

    synonyms = [make_first_upper(name), symbol, make_all_lower(symbol), make_first_upper(make_all_lower(symbol)), name]

    result['synonyms'] = synonyms
    result['value'] = value
    return result


# !ATTENTION! Manual use only!!! #TODO
def configure_crypto_currency_entity():
    url = 'https://api.dialogflow.com/v1'
    headers = {
        'Authorization': 'Bearer {}'.format(DIALOGFLOW_DEV_TOKEN),
        'Content-Type': 'application/json'
    }
    resp = requests.get(url + '/entities', headers=headers)

    # 0 Fiat_currency
    # 1 Cryptocurrency
    # 2 Sorting_parameters
    entity_id = resp.json()[1]['id']

    entities = []
    with open('./cmcapi/currencies.json', 'r') as f:
        data = json.load(f)
    for d in data:
        entities.append(make_simple_entity(d, data[d]))

    resp = requests.post(url + '/entities/' + entity_id + '/entries', headers=headers, json=entities)
    print(resp.json())
