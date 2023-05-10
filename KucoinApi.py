from kucoin.client import Client
import os

class KucoinClient:
    __instance = None

    @staticmethod
    def get_instance():
        """Static method to get the singleton instance of the class."""
        if KucoinClient.__instance is None:
            KucoinClient()
        return KucoinClient.__instance

    def __init__(self):
        """Virtually private constructor."""
        if KucoinClient.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            KucoinClient.__instance = self
            self.__setup_client()

    def __setup_client(self):
        """Private method to setup the Kucoin client."""
        current_folder_path = os.path.dirname(os.path.abspath(__file__))
        api_key, api_secret, api_passphrase = self.__read_config_file(current_folder_path + '/KuCoinCredentials.txt')
        self.client = Client(api_key, api_secret, api_passphrase)

    def __read_config_file(self, file_name):
        """Private method to read the Kucoin credentials from a file."""
        with open(file_name, 'r') as f:
            api_key = ''
            api_secret = ''
            api_passphrase = ''
            for line in f:
                if 'api_key' in line:
                    api_key = line.split('=')[1].strip()
                elif 'api_secret' in line:
                    api_secret = line.split('=')[1].strip()
                elif 'api_passphrase' in line:
                    api_passphrase = line.split('=')[1].strip()
            return api_key, api_secret, api_passphrase

    def withdraw(self, coin, address, amount):
        try:
            result = self.client.create_withdrawal(coin, address, amount)
        except Exception as e:
            print(e)
        else:
            print("Withdrawal request submitted. The details are: ")
            print(result)

    def get_deposit_address(self, coin):
        try:
            result = self.client.get_deposit_address(coin)
        except Exception as e:
            print(e)
        else:
            print(f"Deposit address for {coin} is: {result['address']}")
            return result['address']

    def check_deposit_history(self, coin):
        try:
            result = self.client.get_deposit_page(coin)
        except Exception as e:
            print(e)
        else:
            return result['items']

    def create_order(self, side, amount, symbol):
        try:
            order = None
            if side.lower() == 'buy' or side.lower() == 'sell':
                order = self.client.create_market_order(
                    symbol=symbol,
                    side=side.lower(),
                    size=amount,
                )

            if order is not None:
                print(f'Order {order["orderId"]} has been placed.')
            else:
                print(f'No order was placed. Check the side parameter (buy or sell).')

        except Exception as e:
            print(f'An error occurred while placing the order: {e}')

    #can be made to automatically move other funds into needed coin
    def get_funds(self, coin_pair, buy=True):
        try:
            balances = self.client.get_account_list()
            funds = {balance['currency']: float(balance['balance']) for balance in balances if balance['type'] == 'trade'}
            result = {}
            for asset, balance in funds.items():
                if balance > 0:
                    if buy and coin_pair.endswith(asset):
                        result[asset] = (asset, balance)
                    elif not buy and coin_pair.startswith(asset):
                        result[asset] = (asset, balance)
            return result
        except Exception as e:
            print("Error fetching balance: ", e)
            return None
