from binance.client import Client as BinanceClient
from bybit import bybit as BybitClient
from krakenex import API as KrakenClient
from kucoin.client import Client as KucoinClient
import KucoinApi
import BinanceApi

class ExchangeClientFactory:
    def __init__(self):
        self.clients = {}
    
    def create_client(self, exchange_name):
        if exchange_name in self.clients:
            return self.clients[exchange_name]
        
        exchange_name_lower = exchange_name.lower()
        if exchange_name_lower == 'binance':
            client = BinanceClient.get_instance()
        elif exchange_name_lower == 'kucoin':
            client = KucoinClient.get_instance()
        else:
            raise ValueError(f'Unknown exchange name: {exchange_name}')
            
        self.clients[exchange_name] = client
        return client
