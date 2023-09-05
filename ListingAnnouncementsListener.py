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

def filter_text(text):
    if "🔶#Binance\nBinance Futures Will Launch USDⓈ-M" and "Perpetual Contract" and "Leverage" in text:
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

def open_web_browser_with_binance_page(y):
    webbrowser.open("https://www.binance.com/en/trade/" + y + "?theme=dark&type=spot")

def play_notification_sound():
    winsound.PlaySound("beep.wav", winsound.SND_FILENAME)

# Telegram
# Insert api_id here
api_id = telegram_config.api_id 
# Insert api_hash 'here'
api_hash = telegram_config.api_hash

#Binance
# Insert api_key here
API_key = binance_config.API_key
# Insert secret_key here
secret_key = binance_config.secret_key

# Here you define the target channel that you want to listen to:
user_input_channel = telegram_config.user_input_channel

# Telegram Client
client = TelegramClient('Me', api_id, api_hash)

# Binance Client
binance_client = binance.Client(binance_config.API_key, binance_config.secret_key)
print('Listening started!')

# Listen do messages from target channel
@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    
    # Get message text
    newMessage = event.message.message
    await client.forward_messages(entity='me', messages=event.message)
    print(newMessage)
    play_notification_sound()

    if (filter_text(newMessage)!=""):
        webpage_ticker = filter_text(newMessage)+"_USDT"
        exchange_ticker = filter_text(newMessage)+"USDT"
        buy_on_binance(exchange_ticker)
        open_web_browser_with_binance_page(webpage_ticker)

with client:
    client.run_until_disconnected()