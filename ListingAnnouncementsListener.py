from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)
import webbrowser
import telegram_config

def filter_text(text):
    if "🔶#Binance\nBinance Futures Will Launch USDⓈ-M" and "Perpetual Contract" and "Leverage" in text:
        splited_text = text.split()        
        return splited_text[6]
    else:
        return ""
    
def buy_on_binance(x):
    print("Buy on Binance " + x)

def open_web_browser_with_binance_page(y):
    webbrowser.open("https://www.binance.com/en/trade/" + y + "?theme=dark&type=spot")

# Insert api_id here
api_id = telegram_config.api_id 
# Insert api_hash 'here'
api_hash = telegram_config.api_hash

# Here you define the target channel that you want to listen to:
user_input_channel = telegram_config.user_input_channel

client = TelegramClient('Me', api_id, api_hash)
print('Listening started!')

# Listen do messages from target channel
@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    
    # Get message text
    newMessage = event.message.message
    await client.forward_messages(entity='me', messages=event.message)
    print(newMessage)

    if (filter_text(newMessage)!=""):
        ticker = filter_text(newMessage)+"_USDT"
        print(ticker)
        buy_on_binance(ticker)
        open_web_browser_with_binance_page(ticker)

with client:
    client.run_until_disconnected()