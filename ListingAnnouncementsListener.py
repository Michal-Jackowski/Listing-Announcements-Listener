import base64
import hashlib
import hmac
from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)
import webbrowser
import telegram_config
import binance.client
import binance.enums
import binance_config
import winsound
import re
import path
from kucoin.client import Client
import kucoin_config
import time
import requests

# Telegram
# Insert api_id here
api_id = telegram_config.api_id 
# Insert api_hash 'here'
api_hash = telegram_config.api_hash
# Here you define the target channel that you want to listen to:
user_input_channel = telegram_config.user_input_channel
# Telegram Client
client = TelegramClient('Me', api_id, api_hash)

#Binance
# Insert api_key here
API_key_binance = binance_config.API_key
# Insert secret_key here
secret_key_binance = binance_config.secret_key
# Binance Client
binance_client = binance.Client(API_key_binance, secret_key_binance)

#Kucoin
# Insert api_key here
API_key_kucoin = kucoin_config.API_Key
# Insert secret_key here
API_secret_key_kucoin = kucoin_config.API_Secret_Key
# Insert API passphrase here
API_passphrase_kucoin = kucoin_config.API_Passphrase

kucoin_client = Client(API_key_kucoin, API_secret_key_kucoin, API_passphrase_kucoin)
# Sandbox is under maintenance
#kucoin_client = Client(API_key_kucoin, API_secret_key_kucoin, API_passphrase, sandbox=True)

#Example for get balance of accounts in python
#Try CCXT instead of request
url = 'https://api.kucoin.com/api/v1/accounts'
now = int(time.time() * 1000)
str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
signature = base64.b64encode(hmac.new(API_secret_key_kucoin.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
passphrase = base64.b64encode(hmac.new(API_secret_key_kucoin.encode('utf-8'), API_passphrase_kucoin.encode('utf-8'), hashlib.sha256).digest())
headers = {"KC-API-SIGN": signature, "KC-API-TIMESTAMP": str(now), "KC-API-KEY": API_key_kucoin, "KC-API-PASSPHRASE": passphrase, "KC-API-KEY-VERSION": "2"}
response = requests.request('get', url, headers=headers)
print(response.status_code)
print(response.json())

print('Listening started!')
def open_web_browser_with_binance_page(y):
    webbrowser.open("https://www.binance.com/en/trade/" + y + "?theme=dark&type=spot")

def play_notification_sound():
    notification_sound_path = path.notification_sound_path
    winsound.PlaySound(notification_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

def filter_text(text):
    # Binance Spot Search
    if re.search("Binance Will List", text, re.IGNORECASE):
        # Extract substrings between brackets
        res = re.findall(r'\(.*?\)', text)
        new_text = str(res[0]).replace("(", "")
        new_text2 = new_text.replace(")", "")
        print("Symbol to buy is " + new_text2)
        buy_on_kucoin(new_text2)
        return new_text2
    
    # Coinbase Spot Search
    # "🔵#Coinbase Asset
    # ✨ VTHO VET" => Example

    # Create Mind Map Scheme. Signal => Execution

    # Futures Search
    if re.search("Binance Futures Will Launch USDⓈ-M" and "Perpetual Contract" and "Leverage", text, re.IGNORECASE):
        splited_text = text.split()
        ticker = splited_text[6]
        buy_on_binance(ticker)
        return ticker
    else:
        return ""
    
def buy_on_binance(x):
    # Get average price for x
    avg_price = binance_client.get_avg_price(symbol=x)
    # Get balance for USDT
    balance = binance_client.get_asset_balance(asset='USDT')
    # Buy max for 90% deposit value calculation
    max_buy_quantity = (float(balance["free"]) / float(avg_price["price"])) * 0.9 
    # Round a number to only four decimals:
    max_buy_quantity = round(max_buy_quantity, 4)
    # Buy max for 90% deposit value
    order = binance_client.create_order(symbol = x, side = binance_client.SIDE_BUY, type = binance_client.ORDER_TYPE_MARKET, quantity = max_buy_quantity)    
    print("Bought " + x + " on Binance")

def buy_on_kucoin(x):
    # place a market buy order
    #order = kucoin_client.create_market_order(x, Client.SIDE_BUY, size=0.01)
    #print(order)
    print("Buy " + x + " on Kucoin Exchange!")

# Listen do messages from target channel
@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    
    # Get message text
    newMessage = event.message.message
    # Get private telegram message
    # await client.forward_messages(entity='me', messages=event.message)
    print(newMessage)
    ticker = filter_text(newMessage)
    full_ticker = ticker + "_USDT"
    play_notification_sound()
    open_web_browser_with_binance_page(full_ticker)

with client:
    client.run_until_disconnected()