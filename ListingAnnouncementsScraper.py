from telethon.sync import TelegramClient
import datetime
#import pandas as pd

api_id = ... # Insert api_id here
api_hash = '...' # Insert api_hash 'here'

#chats = ['...'] # Insert chats or channels here, legit one
chats = ['...'] # Insert chats or channels here, just for testing purpose

client = TelegramClient('None', api_id, api_hash)

#df = pd.DataFrame()

print("Press ESC to Stop.")
print("Waiting for Announcements...")

while True:
    for chat in chats:
        with TelegramClient('test', api_id, api_hash) as client:
            for message in client.iter_messages(chat, offset_date=datetime.date.today(), reverse=True):
                print(message.message)
                print(message.date)
                #print(message)
                #data = { "group" : chat, "sender" : message.sender_id, "text" : message.text, "date" : message.date}
                #temp_df = pd.DataFrame(data, index=[1])
                #df = df._append(temp_df)
                
#df['date'] = df['date'].dt.tz_localize(None)
#df.to_excel("...".format(datetime.date.today()), index=False)