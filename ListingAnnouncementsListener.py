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
API_key = binance_config.API_key
# Insert secret_key here
secret_key = binance_config.secret_key
# Binance Client
binance_client = binance.Client(binance_config.API_key, binance_config.secret_key)
print('Listening started!')

def open_web_browser_with_binance_page(y):
    webbrowser.open("https://www.binance.com/en/trade/" + y + "?theme=dark&type=spot")

def play_notification_sound():
    winsound.PlaySound("beep.wav", winsound.SND_FILENAME)

def filter_text(text):
    # Spot Search
    if re.search("Binance Will List", text, re.IGNORECASE):
        # Extract substrings between brackets
        res = re.findall(r'\(.*?\)', text)
        new_text = str(res[0]).replace("(", "")
        new_text2 = new_text.replace(")", "")
        print("Symbol to buy is " + new_text2)
        buy_on_kucoin(new_text2)
        return new_text2

    # Futures Search
    if re.search("Binance Futures Will Launch USDⓈ-M" and "Perpetual Contract" and "Leverage", text, re.IGNORECASE):
        splited_text = text.split()        
        return splited_text[6]
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
    print("Buy " + x + " on Kucoin Exchange!")

# Listen do messages from target channel
@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    
    # Get message text
    newMessage = event.message.message
    # await client.forward_messages(entity='me', messages=event.message)
    print(newMessage)
    play_notification_sound()
    ticker = filter_text(newMessage)
    full_ticker = ticker + "_USDT"
    open_web_browser_with_binance_page(full_ticker)
    # buy_on_binance(ticker)
    # Very slow, average time 2s beetwen printing new message and filter text function

with client:
    client.run_until_disconnected()