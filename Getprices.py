import requests
import json
import time
import threading
from BinanceApi import BinanceClient
from KucoinApi import KucoinClient
from KrakenApi import KrakenClient
from BybitApi import BybitClient
from BitfinexApi import BitfinexClient
import concurrent.futures

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
                
def clean_symbol(symbol):
    return symbol.replace('-', '').replace('_', '').replace(':', '')
    
def get_binance_prices():
    url = 'https://api.binance.com/api/v3/ticker/bookTicker'
    data = fetch_json(url)
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['askPrice']
        bid_price = pair_data['bidPrice']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices
        
def get_bybit_prices():
    url = 'https://api.bybit.com/v2/public/tickers'
    data = fetch_json(url)['result']
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['ask_price']
        bid_price = pair_data['bid_price']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices

def get_kraken_prices():
    url = 'https://api.kraken.com/0/public/Ticker'
    data = fetch_json(url)['result']
    prices = {}
    for pair, pair_data in data.items():
        symbol = pair
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['a'][0]
        bid_price = pair_data['b'][0]
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices

def get_kucoin_prices():
    url = 'https://api.kucoin.com/api/v1/market/allTickers'
    data = fetch_json(url)['data']['ticker']
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['sell']
        bid_price = pair_data['buy']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices

def get_bitfinex_prices():
    url = 'https://api.bitfinex.com/v1/tickers'
    response = fetch_json(url)
    data = response
    
    prices = {}
    for pair_data in data:
        symbol = pair_data['pair']        
        if not symbol.lower().endswith('ust'):
            continue
        ask_price = pair_data['ask']
        bid_price = pair_data['bid']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    
    return prices

def get_superex_prices():
    url = 'https://api.superex.io/v1/tickers'
    response = fetch_json(url)
    data = response['data']
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['sell']
        bid_price = pair_data['buy']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices

def get_hotcoin_prices():
    url = 'https://api.hotcoin.global/v1/tickers'
    response = fetch_json(url)
    data = response['data']
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['sell']
        bid_price = pair_data['buy']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices

def get_citex_prices():
    url = 'https://api.citex.co.kr/v1/tickers'
    response = fetch_json(url)
    data = response['data']
    prices = {}
    for pair_data in data:
        symbol = pair_data['symbol']
        if not symbol.lower().endswith('usdt'):
            continue
        ask_price = pair_data['sell']
        bid_price = pair_data['buy']
        pair = clean_symbol(symbol)
        prices[pair] = {
            'pair': pair,
            'sym': symbol,
            'askPrice': ask_price,
            'bidPrice': bid_price
        }
    return prices


exchange_names = ['Binan', 'Bybit', 'Krake', 'KuCoi', 'Bitfn']


def find_arbitrage_opportunities_parallel(prices):
    matches = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(len(prices)):
            for j in range(i+1, len(prices)):
                if i != j:
                    future = executor.submit(check_prices, prices[i], prices[j])
                    futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None and len(result) > 0:
                matches.append(result)
    return matches

def check_prices(prices1, prices2):
    matches = []
    for key1, price1 in prices1[1].items():
        for key2, price2 in prices2[1].items():
            if price1['pair'] == price2['pair']:
            
                ask_price2 = float(price2['askPrice'])
                bid_price1 = float(price1['bidPrice'])
                
                ask_price1 = float(price1['askPrice'])
                bid_price2 = float(price2['bidPrice'])
                
                if ask_price1 > ask_price2:
                    if ask_price2 > 0.0:
                        diff = (((ask_price1 - ask_price2) / ask_price2 * 100)+((bid_price1 - bid_price2) / bid_price2 * 100))/2
                        if diff > 0.8:
                            match = {
                                'buy_from': exchange_names[prices2[0]],
                                'sell_to': exchange_names[prices1[0]],
                                'bid_from': bid_price2,
                                'ask_from': ask_price2,
                                'bid_to': bid_price1,
                                'ask_to': ask_price1,
                                'symbol_buy': price2['sym'],
                                'symbol_sell': price1['sym'],
                                'sym': price1['pair'],
                                'diff': diff
                            }
                            matches.append(match)
                else:
                    if ask_price1 > 0.0:
                        diff = (((ask_price2 - ask_price1) / ask_price1 * 100)+((bid_price2 - bid_price1) / bid_price1 * 100))/2
                        if diff > 0.8:
                            match = {
                                'buy_from': exchange_names[prices1[0]],
                                'sell_to': exchange_names[prices2[0]],
                                'bid_from': bid_price1,
                                'ask_from': ask_price1,
                                'bid_to': bid_price2,
                                'ask_to': ask_price2,
                                'symbol_buy': price1['sym'],
                                'symbol_sell': price2['sym'],
                                'sym': price1['pair'],
                                'diff': diff
                            }
                            matches.append(match)
    return matches

def move_funds(source_client, destination_client, coin, amount):
    # Withdraw funds from the source client
    source_client.withdraw(coin, destination_client.get_deposit_address(coin), amount)

    # Check the deposit history on the destination client to verify the funds are received
    confirmed = False
    while not confirmed:
        deposit_history = destination_client.check_deposit_history(coin)
        for deposit in deposit_history:
            if deposit['amount'] == amount:
                print(f"Successfully moved {amount} {coin} from {source_client} to {destination_client}")
                return

    print("Failed to move funds.")

if __name__ == '__main__':
    exchanges = [get_bybit_prices, get_bybit_prices, get_kraken_prices, get_kucoin_prices, get_bitfinex_prices]
    while True:
        prices = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(len(exchanges)):
                future = executor.submit(exchanges[i])
                futures.append(future)
            i=0
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                prices.append((i,result))
                i+=1
                
        suggestions = find_arbitrage_opportunities_parallel(prices)
        print('---------------------Arbitrage data----------------------') 
        for suggestion in suggestions:
            for items in suggestion:
                print(items) 
        print('---------------------------------------------------------')    
        
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

