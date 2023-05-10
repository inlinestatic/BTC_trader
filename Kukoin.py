from kucoin.client import Client

# Read config file
def read_config_file(file_name):
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

api_key, api_secret, api_passphrase = read_config_file('KuCoinCredentials.txt')

client = Client(api_key, api_secret, api_passphrase)

# Withdraw function
def withdraw(client, coin, address, amount):
    try:
        result = client.create_withdrawal(coin, address, amount)
    except Exception as e:
        print(e)
    else:
        print("Withdrawal request submitted. The details are: ")
        print(result)

# Get deposit address function
def get_deposit_address(client, coin):
    try:
        result = client.get_deposit_address(coin)
    except Exception as e:
        print(e)
    else:
        print(f"Deposit address for {coin} is: {result['address']}")
        return result['address']

# Check deposit history function
def check_deposit_history(client, coin):
    try:
        result = client.get_deposit_page(coin)
    except Exception as e:
        print(e)
    else:
        return result['items']

# Create order function
def create_order(client, side, amount, symbol):
    try:
        order = None
        if side.lower() == 'buy' or side.lower() == 'sell':
            order = client.create_market_order(
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

# Usage
# create_order(client, 'buy', 0.001)

# Usage
# withdraw(client, 'BTC', 'YOUR_BTC_ADDRESS', 0.001)
# get_deposit_address(client, 'BTC')
# check_deposit_history(client, 'BTC')
