from bybit import bybit

# Read config file
def read_config_file(file_name):
    with open(file_name, 'r') as f:
        api_key = ''
        api_secret = ''
        for line in f:
            if 'api_key' in line:
                api_key = line.split('=')[1].strip()
            elif 'api_secret' in line:
                api_secret = line.split('=')[1].strip()
        return api_key, api_secret

api_key, api_secret = read_config_file('BybitCredentials.txt')

client = bybit(test=False, api_key=api_key, api_secret=api_secret)

# Get wallet balance function
def get_wallet_balance(client, coin):
    try:
        result = client.Wallet.Wallet_getBalance(coin=coin).result()
    except Exception as e:
        print(e)
    else:
        print(f"Wallet balance for {coin} is: {result[0]['result'][coin]['equity']}")
        return result[0]['result'][coin]['equity']

# Check withdrawal history function
def check_withdraw_history(client, coin):
    try:
        result = client.Wallet.Wallet_getWithdrawHistory(coin=coin).result()
    except Exception as e:
        print(e)
    else:
        return result[0]['result']['data']

# Usage
# get_wallet_balance(client, 'BTC')
# check_withdraw_history(client, 'BTC')
