from binance.client import Client
import os

class BinanceClient:
    _instance = None

    @staticmethod
    def get_instance():
        if BinanceClient._instance is None:
            BinanceClient()
        return BinanceClient._instance

    def __init__(self):
        if BinanceClient._instance is not None:
            raise Exception("BinanceClient is a singleton class")
        else:
            self._api_key, self._api_secret = self._read_config_file()
            self.client = Client(self._api_key, self._api_secret, tld='us')
            BinanceClient._instance = self

    def _read_config_file(self):
        current_folder_path = os.path.dirname(os.path.abspath(__file__))
        credentials_file_path = os.path.join(current_folder_path, 'BinanceCredentials.txt')
        with open(credentials_file_path, 'r') as f:
            api_key = ''
            api_secret = ''
            for line in f:
                if 'api_key' in line:
                    api_key = line.split('=')[1].strip()
                elif 'api_secret' in line:
                    api_secret = line.split('=')[1].strip()
            return api_key, api_secret

    def withdraw(self, asset, address, amount):
        try:
            result = self.client.withdraw(
                asset=asset,
                address=address,
                amount=amount
            )
        except Exception as e:
            print(e)
        else:
            print("Withdrawal request submitted. The details are: ")
            print(result)

    def get_deposit_address(self, asset):
        try:
            result = self.client.get_deposit_address(asset=asset)
        except Exception as e:
            print(e)
        else:
            print(f"Deposit address for {asset} is: {result['address']}")
            return result['address']

    def check_deposit_history(self, asset):
        try:
            result = self.client.get_deposit_history(asset=asset)
        except Exception as e:
            print(e)
        else:
            return result['depositList']
        
    def create_order(self, side, amount, symbol):
        try:
            order = None
            if side.lower() == 'buy' or side.lower() == 'sell':
                order = self.client.create_order(
                    symbol=symbol,
                    type='market',
                    side=side.lower(),
                    quantity=amount,
                    params={},
                )

            if order is not None:
                print(f'Order {order["id"]} has been placed.')
            else:
                print(f'No order was placed. Check the side parameter (buy or sell).')

        except Exception as e:
            print(f'An error occurred while placing the order: {e}')

    #can be made to automatically move other funds into needed coin
    def get_funds(self, coin_pair, buy=True):
        try:
            balances = self.client.fetch_balance()
            funds = balances['info']['balances']
            result = {}
            for fund in funds:
                asset = fund['asset']
                free = float(fund['free'])
                if free > 0.0:
                    if buy == True:
                        if coin_pair.toupper().endswith(asset.toupper()):
                            result = (asset, free)
                        elif coin_pair.toupper().startswith(asset.toupper()):
                            result = (asset, free)
            return result
        except Exception as e:
            print("Error fetching balance: ", e)
            return None
    