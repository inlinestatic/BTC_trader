import bitfinex

class BitfinexClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = bitfinex.Client(api_key=self.api_key, api_secret=self.api_secret)

    def withdraw(self, currency, address, amount):
        try:
            result = self.client.withdraw(currency, address, amount)
            print("Withdrawal request submitted. The details are:")
            print(result)
        except Exception as e:
            print("Error submitting withdrawal request:", e)

    def get_deposit_address(self, currency):
        try:
            result = self.client.get_deposit_address(currency)
            print(f"Deposit address for {currency} is: {result['address']}")
            return result['address']
        except Exception as e:
            print("Error fetching deposit address:", e)
            return None

    def check_deposit_history(self, currency):
        try:
            result = self.client.get_deposit_history(currency)
            return result
        except Exception as e:
            print("Error fetching deposit history:", e)
            return None

    def create_order(self, symbol, amount, price, side, order_type='LIMIT', **kwargs):
        try:
            order_params = {
                'symbol': symbol,
                'amount': str(amount),
                'price': str(price),
                'side': side,
                'type': order_type,
                **kwargs
            }
            order_response = self.client.new_order(**order_params)
            print("Order response:")
            print(order_response)
        except Exception as e:
            print("Error creating order:", e)

    def get_funds(self, coin_pair, buy=True):
        try:
            balances = self.client.balances()
            result = {}
            for balance in balances:
                asset = balance['currency']
                free = float(balance['available'])
                if free > 0.0:
                    if buy and coin_pair.endswith(asset.upper()):
                        result[asset] = (asset, free)
                    elif not buy and coin_pair.startswith(asset.upper()):
                        result[asset] = (asset, free)
            return result
        except Exception as e:
            print("Error fetching funds:", e)
            return None
