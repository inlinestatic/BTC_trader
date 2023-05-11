import requests
import time
import hashlib
import hmac
import base64

class KrakenClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.kraken.com'

    def get_balances(self):
        endpoint = '/0/private/Balance'
        nonce, signature = self.__generate_signature(endpoint)
        data = {
            'nonce': nonce
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': signature
        }
        response = requests.post(self.base_url + endpoint, data=data, headers=headers)
        result = response.json()
        if 'error' in result:
            print("Error fetching balances: ", result['error'])
            return None
        balances = result['result']
        return balances

    def get_tradeable_pairs(self):
        endpoint = '/0/public/AssetPairs'
        response = requests.get(self.base_url + endpoint)
        result = response.json()
        if 'error' in result:
            print("Error fetching tradeable pairs: ", result['error'])
            return None
        pairs = result['result']
        return pairs

    def create_order(self, pair, side, volume, price, type='limit'):
        endpoint = '/0/private/AddOrder'
        nonce, signature = self.__generate_signature(endpoint)
        data = {
            'nonce': nonce,
            'pair': pair,
            'type': side,
            'ordertype': type,
            'price': price,
            'volume': volume
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': signature
        }
        response = requests.post(self.base_url + endpoint, data=data, headers=headers)
        result = response.json()
        if 'error' in result:
            print("Error creating order: ", result['error'])
            return None
        return result

    def __generate_signature(self, endpoint):
        nonce = str(int(time.time() * 1000))
        message = endpoint.encode() + hashlib.sha256(nonce.encode() + endpoint.encode()).digest()
        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        signature = base64.b64encode(signature.digest()).decode()
        return nonce, signature

    def get_funds(self, coin_pair, buy=True):
        try:
            response = self.client.query_private('Balance')
            if 'result' in response and 'error' not in response['result']:
                funds = response['result']
                result = {}
                for asset, balance in funds.items():
                    if asset != 'ZUSD' and asset != 'ZEUR':  # Exclude fiat currencies
                        available_balance = float(balance)
                        if buy:
                            if coin_pair.endswith(asset) or coin_pair.startswith(asset):
                                result[asset] = available_balance
                        else:
                            if not coin_pair.endswith(asset) and not coin_pair.startswith(asset):
                                result[asset] = available_balance
                return result
            else:
                print("Failed to fetch funds: ", response['error'])
        except Exception as e:
            print("Error fetching funds: ", e)
            return None