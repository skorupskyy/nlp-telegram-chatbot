from bot.local_settings import X_CMC_PRO_API_KEY

latest_quotes_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?'

headers = {
 'Accept': 'application/json',
 'Accept-Encoding': 'deflate, gzip',
 'X-CMC_PRO_API_KEY': X_CMC_PRO_API_KEY,
}
