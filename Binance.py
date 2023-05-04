import sys
import ccxt
import time
import os.path
import pickle
import base64
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


GoogleCreds = None
SCOPES = 'https://mail.google.com/'
request = google.auth.transport.requests.Request()

client = None

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

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(request)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GoogleCreds, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def read_last_message(service, user_id):
    query = "from:noreply@tradingview.com subject:Alert"
    results = service.users().messages().list(userId=user_id, q=query, maxResults=1).execute()
    messages = results.get('messages', [])
    message_body = ""
    if not messages:
        return ""

    message = service.users().messages().get(userId=user_id, id=messages[0]['id']).execute()
    is_unread = 'UNREAD' in message['labelIds']

    if is_unread:
        payload = message['payload']
        if 'parts' in payload:
            parts = payload['parts']
            data = ''
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    break
            if not data:
                return ""

            message_body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            message_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        if 'Short position entered!' in message_body:
            message_body = 'Short position entered!'
        else:
            message_body = 'Long position entered!'
        service.users().messages().delete(
            userId=user_id,
            id=message['id']
        ).execute()
        
    return message_body

def get_funds():
    try:
        balances = client.fetch_balance()
        funds = balances['info']['balances']
        usd_balance = 0
        btc_balance = 0
        for fund in funds:
            asset = fund['asset']
            free = float(fund['free'])
            locked = float(fund['locked'])
            if free > 0 or locked > 0:
                if asset == 'USD':
                    usd_balance = free + locked
                elif asset == 'BTC':
                    btc_balance = free + locked
        return {'USD': usd_balance, 'BTC': btc_balance}
    except Exception as e:
        print("Error fetching balance: ", e)
        return None
        
def create_order(side, amount):
    try:
        if side == 'buy':
            order = client.create_order(
                symbol='BTC/USD',
                type='market',
                side=side,
                amount=amount,
                params={},
            )
        elif side == 'sell':
            order = client.create_order(
                symbol='BTC/USD',
                type='market',
                side=side,
                amount=amount,
                params={},
            )
        print(f'Order {order["id"]} has been placed.')
    except Exception as e:
        print(f'An error occurred while placing the order: {e}')
        
def main():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    user_id = 'me'
    
    while True:
        try:
            #TradingView alert - time to enter long or short
            output = read_last_message(service, user_id)  
            # Get BTC/USD ticker information
            ticker = client.fetch_ticker('BTC/USD')
            # Get current traded price of BTC in USD
            current_price_usd = ticker['last']   
            print(f"BTC/USD Price: {current_price_usd}")
            if output != "":
                print(f'--------------------------------------------------')
                print(f"|{output}")
                
                # Get the last trade executed on Binance
                trades = client.fetch_my_trades(symbol='BTC/USDT', limit=1)
                   
                # Check available funds
                funds  = get_funds()
                print(f"|{funds}")
                
                if len(trades) > 0:
                    last_trade = trades[0]
                    last_trade_side = last_trade['side']
                    last_trade_price = last_trade['price']
                    print(f"|Last side: {last_trade_side}")
                    print(f"|Current Price: {current_price_usd}")
                    print(f"|Last price: {last_trade_price}")
                    
                    #account fee
                    diviation = 1-min(current_price_usd, last_trade_price)/max(current_price_usd, last_trade_price)
                    
                    if diviation>0.01 :
                        if "long" in output.lower() and last_trade_side == 'sell':  
                            # Here we use all available USD to buy BTC
                            create_order('buy', funds['USD']/1.001)
                            print(f'|Bought')                        
                        elif "short" in output.lower() and last_trade_side == 'buy':
                            # Here we sell all available BTC
                            create_order('sell', funds['BTC']/1.001)
                            print(f'|Sold')                                         
                    print(f'--------------------------------------------------')
                    print(f'')
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(60)
 
if __name__ == '__main__':
    GoogleCreds = sys.argv[1]
    BinanceCreds = sys.argv[2]
    print(sys.argv)
    api_key, api_secret = read_config_file(BinanceCreds)
    client = ccxt.binanceus({ 'apiKey': api_key, 'secret': api_secret, })
    main()