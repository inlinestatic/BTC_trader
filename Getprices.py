import requests
import json
import time
import threading
from BinanceApi import BinanceClient
from KucoinApi import KucoinClient

from concurrent.futures import ThreadPoolExecutor

def fetch_json(url):
    for attempt in range(3):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception if the status code is not 200
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # Not found, not retriable
                raise
            else:
                # Retriable error, wait for 1 second before retrying
                if attempt < 2:
                    print(f'Retryable error occurred, retrying in 1 second... (attempt {attempt+1}/3)')
                    time.sleep(1)
                else:
                    raise e
        except Exception as e:
            # Other errors, wait for 1 second before retrying
            if attempt < 2:
                print(f'Unexpected error occurred, retrying in 1 second... (attempt {attempt+1}/3)')
                time.sleep(1)
            else:
                raise e

def fetch_data_binance():
    try:
        #data = fetch_json('https://api.binance.us/api/v3/ticker/price')        
        book_data = fetch_json('https://api.binance.us/api/v3/ticker/bookTicker')
        #book_dict = {info['symbol'] for info in book_data if float(info["bidQty"])!=0}

        # Get the current prices for all USD pairs
        usd_pairs_prices = {}
        for pair in book_data:
            if float(pair["bidQty"])!=0:
                usd_pairs_prices.update({pair['symbol'].upper(): (pair['symbol'],float(pair['bidPrice']))})
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Binance HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Binance Other error occurred: {err}')  # Any other exception
        
def fetch_data_bybit():
    try:
        data = fetch_json('https://api.bybit.com/v2/public/tickers')

        usd_pairs_prices = {}
        for pair in data["result"]:
            pair_name = pair['symbol']
            usd_pairs_prices.update({pair_name.upper(): (pair_name, float(pair['last_price']))})
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Bybit HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Bybit Other error occurred: {err}')  # Any other exception

def fetch_data_kraken():
    try:
        data = fetch_json('https://api.kraken.com/0/public/Ticker')
        pairs_prices = {}
        for pair, info in data["result"].items():
            last_trade_price = float(info['c'][0])  # 'c' is the field for last trade closed price in Kraken API
            pairs_prices.update({pair.upper(): (pair, last_trade_price)})
        return pairs_prices

    except requests.HTTPError as http_err:
        print(f'Kraken HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Kraken Other error occurred: {err}')  # Any other exception

def fetch_data_kucoin():
    try:
        data = fetch_json('https://api.kucoin.com/api/v1/market/allTickers')

        pairs_prices = {}
        for info in data["data"]["ticker"]:
            if info['last'] is not None:
                symbol = info['symbol'].replace('-','')            
                last_price = float(info['last'])  # 'last' is the field for last price in KuCoin API
                pairs_prices.update({symbol.upper(): (info['symbol'], last_price)})
        return pairs_prices

    except requests.HTTPError as http_err:
        print(f'KuCoin HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'KuCoin Other error occurred: {err}')  # Any other exception

if __name__ == "__main__":
    exchange_names = ['Binance', 'Bybit', 'Kraken', 'KuCoin']
    exchanges = [fetch_data_binance, fetch_data_bybit, fetch_data_kraken, fetch_data_kucoin]

    #exchange_names = ['Binance', 'KuCoin']
    #exchanges = [fetch_data_binance, fetch_data_kucoin]
    
    exchane_id = 0
    while True:
        with ThreadPoolExecutor(max_workers=len(exchanges)) as executor:
            results = list(executor.map(lambda f: f(), exchanges))
        
        exchanges_result = {i: result for i, result in enumerate(results)}
        price_symbol_map = {}
        for i, exchange_pairs in exchanges_result.items():
            for exchange_name, (symbol, price) in exchange_pairs.items():
                if exchange_name not in price_symbol_map:
                    price_symbol_map[exchange_name] = {'prices': [0.0]*len(exchanges), 'symbols': ['']*len(exchanges)}
                price_symbol_map[exchange_name]['prices'][i] = price
                price_symbol_map[exchange_name]['symbols'][i] = symbol
        
        to_add = list()
        for pair, data in price_symbol_map.items():
            prices = data['prices']
            symbols = data['symbols']
            min_val = min((price for price in prices if price != 0), default=float('inf'))
            max_val = max(prices)
        
            if min_val > 0 and max_val > 0 and min_val != max_val:
                percentile_diff = ((max_val - min_val) / min_val) * 100
                if 2 < percentile_diff < 20:
                    min_index = prices.index(min_val)
                    max_index = prices.index(max_val)
                    trade = {
                        'buy_from': exchange_names[min_index],
                        'buy_symbol': symbols[min_index],
                        'sell_to': exchange_names[max_index],
                        'sell_symbol': symbols[max_index],
                        'buy_price': min_val,
                        'sell_price': max_val,
                        'diff': percentile_diff
                    }
                    to_add.append(trade)
                    print(trade)
        to_add.sort(key=lambda x: x['diff'], reverse=True)
        
        #current_trade = None
        #for trade in to_add:
        #    #print(trade)
        #    if trade['buy_from'] == exchange_names[exchane_id]:
        #        current_trade = trade 
        #        break
        #client1 = None
        #client2 = None
        #if exchane_id == 0:
        #    client1 = BinanceClient.get_instance()
        #    client2 = KucoinClient.get_instance()
        #else:
        #    client2 = BinanceClient.get_instance()
        #    client1 = KucoinClient.get_instance()
            
        #if current_trade is not None:
        #    fund = client1.get_funds(current_trade['buy_symbol'], buy=True)
        #    #POSSIBLY NEED TO ACCOUNT FOR FEES
        #    print('Buy {fund[0]} from {current_trade['buy_from']} ammount {fund[1]}')
        #    if fund[1]>0:
        #        ammount = (fund[1] - fund[1]*0.0001)/current_trade['buy_price']
        #        client1.create_order('buy', ammount, current_trade['buy_symbol'])
        #   
        #exchane_id = (exchane_id + 1) % 2
        #print(i)

