import bybit
import os

class BybitClient:
    __instance = None

    @staticmethod
    def get_instance():
        """Static method to get the singleton instance of the class."""
        if BybitClient.__instance is None:
            BybitClient()
        return BybitClient.__instance

    def __init__(self):
        """Virtually private constructor."""
        if BybitClient.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            BybitClient.__instance = self
            self.__setup_client()

    def __setup_client(self):
        """Private method to setup the Bybit client."""
        current_folder_path = os.path.dirname(os.path.abspath(__file__))
        api_key, api_secret = self.__read_config_file(current_folder_path + '/BybitCredentials.txt')
        self.client = BybitClient(api_key, api_secret)

    def __read_config_file(self, file_name):
        """Private method to read the Bybit credentials from a file."""
        with open(file_name, 'r') as f:
            api_key = ''
            api_secret = ''
            for line in f:
                if 'api_key' in line:
                    api_key = line.split('=')[1].strip()
                elif 'api_secret' in line:
                    api_secret = line.split('=')[1].strip()
            return api_key, api_secret

    def withdraw_funds(self, coin, address, amount):
        try:
            result = self.client.wallet.withdraw(coin, address, amount)
            if result['ret_code'] == 0:
                print("Withdrawal request submitted. The details are:")
                print(result)
            else:
                print("Error occurred while withdrawing funds.")
                print(result['ret_msg'])
        except Exception as e:
            print(f"Error occurred while withdrawing funds: {e}")

    def get_deposit_address(self, coin):
        try:
            result = self.client.wallet.get_deposit_address(coin)
            if result['ret_code'] == 0:
                deposit_address = result['result']['address']
                print(f"Deposit address for {coin} is: {deposit_address}")
                return deposit_address
            else:
                print("Error occurred while getting deposit address.")
                print(result['ret_msg'])
                return None
        except Exception as e:
            print(f"Error occurred while getting deposit address: {e}")
            return None

    def check_deposit_history(self, coin):
        try:
            result = self.client.wallet.get_deposit_list(coin)
            if result['ret_code'] == 0:
                deposit_history = result['result']
                return deposit_history
            else:
                print("Error occurred while checking deposit history.")
                print(result['ret_msg'])
                return None
        except Exception as e:
            print(f"Error occurred while checking deposit history: {e}")
            return None

    def create_order(self, side, amount, symbol):
        try:
            if side.lower() not in ['buy', 'sell']:
                print("Invalid side parameter. Should be 'buy' or 'sell'.")
                return

            result = self.client.place_active_order(symbol=symbol, side=side.lower(), qty=amount)
            if result['ret_code'] == 0:
                order_id = result['result']['order_id']
                print(f"Order {order_id} has been placed.")
            else:
                print("Error occurred while placing the order.")
                print(result['ret_msg'])
        except Exception as e:
            print(f"An error occurred while placing the order: {e}")

    def get_funds(self, coin_pair, buy=True):
        try:
            response = self.client.Wallet.Wallet_getBalance().result()
            if response['ret_code'] == 0:
                funds = response['result']
                result = {}
                for fund in funds:
                    asset = fund['coin']
                    available_balance = fund['available_balance']
                    if buy:
                        if coin_pair.endswith(asset) or coin_pair.startswith(asset):
                            result[asset] = available_balance
                    else:
                        if not coin_pair.endswith(asset) and not coin_pair.startswith(asset):
                            result[asset] = available_balance
                return result
            else:
                print("Failed to fetch funds: ", response['ret_msg'])
        except Exception as e:
            print("Error fetching funds: ", e)
            return None