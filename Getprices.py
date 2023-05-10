import requests
import json
import time
import threading
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


def fetch_chunk_yobit(usd_pairs, i):
    chunk_pairs = usd_pairs[i*20:i*20+20]
    pairs_str = '-'.join(chunk_pairs)
    for attempt in range(3):
        pairs_prices = {}
        try:
            chunk_data = fetch_json(f'https://yobit.net/api/3/ticker/{pairs_str}')
            for pair in chunk_data:
                pairtrim = pair.replace('_','')                
                pairs_prices.update({pairtrim.upper(): (pair,chunk_data[pair]['last'])})
            return pairs_prices
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
    
def fetch_data_yobit():
    try:
        start_time = time.time()
        data = fetch_json('https://yobit.net/api/3/info')

        usd_pairs = [pair for pair in data['pairs']]
        print(f'Count of yobit pairs: {len(usd_pairs)}')

        usd_pairs_prices = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = []
            chunks = int(len(usd_pairs)/20)
            if len(usd_pairs)%20>0:
                chunks += 1
            # Split pairs into chunks of 20
            for i in range(chunks):
                results.append(executor.submit(fetch_chunk_yobit, usd_pairs, i))

            for result in results:
                chunk_pairs = result.result()
                usd_pairs_prices.update(chunk_pairs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Yobit: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Yobit HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Yobit Other error occurred: {err}')  # Any other exception
        

def fetch_data_sonitix():
    try:
        start_time = time.time()
        usd_pairs_prices = {}
        chunk_data = fetch_json(f'https://api.sonitix.exchange/api/Public/Ticker')
        print(f'Count of sonitix pairs: {len(chunk_data)}')
        for pairs in chunk_data:
            for pair in pairs.keys():
                pairtrim = pair.replace('/','')
                usd_pairs_prices.update({pairtrim.upper(): (pair,float(pairs[pair]['last_price']))})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Sonitix: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Sonitix HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Sonitix Other error occurred: {err}')  # Any other exception
        
def fetch_data_binance():
    try:
        start_time = time.time()
        data = fetch_json('https://api.binance.us/api/v3/ticker/price')        
        book_data = fetch_json('https://api.binance.us/api/v3/ticker/bookTicker')
        book_dict = {info['symbol'] for info in book_data if float(info["bidQty"])!=0}
        print(f'Count of binance pairs: {len(book_dict)}')

        # Get the current prices for all USD pairs
        usd_pairs_prices = {}
        for pair in data:
            if pair['symbol'] in book_dict:
                usd_pairs_prices.update({pair['symbol'].upper(): (pair['symbol'],float(pair['price']))})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Binance: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Binance HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Binance Other error occurred: {err}')  # Any other exception

def fetch_data_gopax():
    try:
        start_time = time.time()
        data = fetch_json('https://api.gopax.co.kr/trading-pairs/stats')

        print(f'Count of gopax pairs: {len(data)}')

        usd_pairs_prices = {}
        for pair in data:
            pairtrim = pair['name'].replace('-','')
            usd_pairs_prices.update({pairtrim.upper(): (pair, float(pair['open']))})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Gopax: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'GOPAX HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'GOPAX Other error occurred: {err}')  # Any other exception
        
def fetch_data_unitedexchange():
    try:
        start_time = time.time()
        usd_pairs_prices = {}
        chunk_data = fetch_json('https://unitedexchange.in/api-ticker')
        print(f'Count of unitedexchange pairs: {len(chunk_data)}')
        for item in chunk_data:
            pairtrim = item['ticker_id'].replace('_','')
            usd_pairs_prices.update({pairtrim.upper(): (item['ticker_id'],float(item['last_price']))})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"UnitedExchange: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'unitedexchange HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'unitedexchange Other error occurred: {err}')  # Any other exception

def fetch_data_bitcovia():
    try:
        start_time = time.time()
        data = fetch_json('https://api.bitcoiva.com/tickers')

        usd_pairs_prices = {}
        for pairs in data['data']['tickers'].items():
            if 'last' in pairs[1]:
                pairname = pairs[1]['symbol'].replace('-','')
                usd_pairs_prices.update({pairname.upper(): ( pairs[1]['symbol'], float(pairs[1]['last']))}) #see https://api.bitcoiva.com/tickers

        print(f'Count of bitcovia pairs: {len(usd_pairs_prices)}')
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Bitcovina: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Bitcovia HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Bitcovia Other error occurred: {err}')  # Any other exception
        
def fetch_data_bybit():
    try:
        start_time = time.time()
        data = fetch_json('https://api.bybit.com/v2/public/tickers')

        print(f'Count of Bybit pairs: {len(data["result"])}')

        usd_pairs_prices = {}
        for pair in data["result"]:
            pair_name = pair['symbol']
            usd_pairs_prices.update({pair_name.upper(): (pair_name, float(pair['last_price']))})

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Bybit: Elapsed time: {elapsed_time} seconds")
        return usd_pairs_prices

    except requests.HTTPError as http_err:
        print(f'Bybit HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Bybit Other error occurred: {err}')  # Any other exception

def fetch_data_kraken():
    try:
        start_time = time.time()
        data = fetch_json('https://api.kraken.com/0/public/Ticker')
        print(f'Count of Kraken pairs: {len(data["result"])}')

        pairs_prices = {}
        for pair, info in data["result"].items():
            last_trade_price = float(info['c'][0])  # 'c' is the field for last trade closed price in Kraken API
            pairs_prices.update({pair.upper(): (pair, last_trade_price)})

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Kraken: Elapsed time: {elapsed_time} seconds")
        return pairs_prices

    except requests.HTTPError as http_err:
        print(f'Kraken HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'Kraken Other error occurred: {err}')  # Any other exception

def fetch_data_kucoin():
    try:
        start_time = time.time()
        data = fetch_json('https://api.kucoin.com/api/v1/market/allTickers')

        print(f'Count of KuCoin pairs: {len(data["data"]["ticker"])}')

        pairs_prices = {}
        for info in data["data"]["ticker"]:
            if info['last'] is not None:
                symbol = info['symbol'].replace('-','')            
                last_price = float(info['last'])  # 'last' is the field for last price in KuCoin API
                pairs_prices.update({symbol.upper(): (info['symbol'], last_price)})

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"KuCoin: Elapsed time: {elapsed_time} seconds")
        return pairs_prices

    except requests.HTTPError as http_err:
        print(f'KuCoin HTTP error occurred: {http_err}')  # The request returned an unsuccessful status code
    except Exception as err:
        print(f'KuCoin Other error occurred: {err}')  # Any other exception

if __name__ == "__main__":  
    start_time = time.time() 
    exchange_names = [ 'Binance', 'bybit', 'kraken', 'kucoin']    
    exchanges = [ fetch_data_binance, fetch_data_bybit, fetch_data_kraken, fetch_data_kucoin]

    with ThreadPoolExecutor(max_workers=len(exchanges)) as executor:
        results = [executor.submit(exchange) for exchange in exchanges]

    pairs = {}
    for i, exchange in enumerate(exchanges):
        pairs[i] = results[i].result()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Cumulative: Elapsed time: {elapsed_time} seconds")
    merged_pairs = {}
    for i, exchange_pairs in pairs.items():
        for pair, price in exchange_pairs.items():
            if pair not in merged_pairs:
                merged_pairs[pair] = [0.0] * len(exchanges)
            merged_pairs[pair][i] = price[1]
    #for pair in merged_pairs:
    #    print(pair)
    to_add = {}
    for pair, prices in merged_pairs.items():
        non_zero_numbers = [num for num in prices if num != 0]
        if len(non_zero_numbers) != 0:
            min_val = min(non_zero_numbers)
            max_val = max(prices)
            if min_val > 0.0 and max_val > 0 and min_val != max_val:            
                percentile_diff = ((max_val - min_val) / min_val) * 100
                if percentile_diff > 5:
                    min_index = prices.index(min_val)
                    max_index = prices.index(max_val)
                    trade = f'{pair} Buy from {exchange_names[min_index]}, Sell to {exchange_names[max_index]}, Diff = {percentile_diff:.2f}%'
                    to_add[pair] = trade
                    print(trade)

    time.sleep(30)
