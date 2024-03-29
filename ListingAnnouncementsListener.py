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
import ccxt
from time import strftime, localtime

# Telegram
# Insert api_id here
api_id = telegram_config.api_id 
# Insert api_hash 'here'
api_hash = telegram_config.api_hash
# Here you define the target channel that you want to listen to:
#user_input_channel = telegram_config.user_input_channel
user_input_channel = telegram_config.test_user_input_channel
# Telegram Client
telegram_client = TelegramClient('Me', api_id, api_hash)

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

kucoin_exchange_authentification = {
    'apiKey': API_key_kucoin,
    'secret': API_secret_key_kucoin,
    'password' : API_passphrase_kucoin
}
kucoin_client = ccxt.kucoin(kucoin_exchange_authentification)
print('Listening started!')

def open_web_browser_with_exchange_page(ticker, exchange):
    if exchange == "Binance":
        webbrowser.open("https://www.binance.com/en/trade/" + ticker + "?theme=dark&type=spot")
    if exchange == "Kucoin":
        webbrowser.open("https://www.kucoin.com/trade/" + ticker)

def play_notification_sound():
    notification_sound_path = path.notification_sound_path
    winsound.PlaySound(notification_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

def save_logs_to_a_file(path, text):
    f = open(path, "a")
    f.write(text)
    f.close()

def get_time_execution_result(start, end, signal, exchange):
    result = round((end - start), 2)
    start_date_time = strftime('%m-%d-%Y %H:%M:%S', localtime(start))
    return "[" + start_date_time + "]" + " Time beetwen filter text function on " + signal + " and buy market order on " + exchange + " is equal to " + str(result) + "\n"

def filter_text(text):
    # Binance Spot Search
    if re.search("Binance Will List", text, re.IGNORECASE):
        # Measure time after filter text
        start = time.time()
        # Extract substrings between brackets
        res = re.findall(r'\(.*?\)', text)
        new_text = str(res[0]).replace("(", "")
        new_text2 = new_text.replace(")", "")
        print("Symbol to buy is " + new_text2)
        full_ticker = new_text2 + "-USDT"
        buy_on_kucoin(full_ticker)
        # Measure time after successful buy
        end = time.time()
        save_logs_to_a_file(path.kucoin_execution_time_logs, get_time_execution_result(start, end, "(Binance Spot)", "(Kucoin)"))
        open_web_browser_with_exchange_page(full_ticker, "Kucoin")
        return 0
    
    # Coinbase Spot Search
    if re.search("Coinbase Asset", text, re.IGNORECASE):
        # Measure time after filter text
        start = time.time()
        # Splitting text
        splited_text = text.split()
        ticker = splited_text[3]
        full_ticker = ticker + "-USDT"
        buy_on_kucoin(full_ticker)
        # Measure time after successful buy
        end = time.time()
        save_logs_to_a_file(path.kucoin_execution_time_logs, get_time_execution_result(start, end, "(Coinbase Spot)", "(Kucoin)"))
        open_web_browser_with_exchange_page(full_ticker, "Kucoin")
        return 0

    # Futures Search
    if re.search("Binance Futures Will Launch USDⓈ-M", text, re.IGNORECASE): # Temporary solution, not super efficient but works
        if re.search("Perpetual Contract", text, re.IGNORECASE):
            if re.search("Leverage", text, re.IGNORECASE):
                # Measure time after filter text
                start = time.time()
                splited_text = text.split()
                ticker = splited_text[6]
                buy_on_binance(ticker)
                # Measure time after successful buy
                end = time.time()
                save_logs_to_a_file(path.binance_execution_time_logs, get_time_execution_result(start, end, "(Binance Futures)", "(Binance)"))
                full_ticker = ticker + "_USDT"
                open_web_browser_with_exchange_page(full_ticker, "Binance")
                print("Done")
                return 0
    
def buy_on_binance(x):
    # Strange. First order is slow average 1-1.5 seconds but others are faster 0.5-0.6 seconds.
    # Get average price for x
    avg_price = binance_client.get_avg_price(symbol=x + "USDT")
    # Get balance for USDT
    balance = binance_client.get_asset_balance(asset='USDT')
    # Round a number to only four decimals:
    max_buy_quantity = round(calculate_buy_order_quantity(balance["free"], avg_price["price"], 0.5), 4)
    # Buy max for 90% deposit value
    order = binance_client.create_order(symbol = x + "USDT", side = binance_client.SIDE_BUY, type = binance_client.ORDER_TYPE_MARKET, quantity = max_buy_quantity)    
    print("Bought " + x + " on Binance")

def buy_on_kucoin(x):    
    # Strange. First order is slow average 3-4 seconds but others are faster 0.5-1 seconds.
    # Get last price for x
    y = kucoin_client.fetch_ticker(x)
    last_price = y["last"]
    # Get balance for USDT
    usdt_balance_dictionary = kucoin_client.fetch_balance()["USDT"]
    free_usdt_balance = usdt_balance_dictionary["free"]
    # Round a number to only four decimals:
    max_buy_quantity = round(calculate_buy_order_quantity(free_usdt_balance, last_price, 0.5), 4)
    # Buy max for 90% deposit value
    order = kucoin_client.create_market_buy_order(x, max_buy_quantity)
    print("Bough " + x + " on Kucoin Exchange!")

def cancel_all_order_on_kucoin(x):
    kucoin_client.cancel_all_orders(x)

def calculate_buy_order_quantity(balance, price, percentage):
    max_buy_quantity = (float(balance) / float(price)) * percentage 
    return max_buy_quantity

# Listen do messages from target channel
@telegram_client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    # Get message text
    newMessage = event.message.message
    print(newMessage)
    filter_text(newMessage)
    play_notification_sound()

with telegram_client:
    telegram_client.run_until_disconnected()