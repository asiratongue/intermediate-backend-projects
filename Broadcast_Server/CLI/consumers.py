import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from .models import chat_history
from asgiref.sync import sync_to_async, SyncToAsync

message_history_dict = {}
SyncToAsync.thread_sensitive = False 
PRE_SHARED_KEY = 'CONGLOMERATE'
class BrowserConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_group_name = 'group_chat'

        QueryString = parse_qs(self.scope["query_string"].decode())
        psk = QueryString.get("psk", [None])[0]

        if psk != PRE_SHARED_KEY:
            await self.accept()
            await self.send("haha wrong key [OMITTED]!")
            await self.close()  

        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)  #adding ws connection to the group 'nicechat',each ws connection assigned a unique channel_name
            await self.accept()



    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):

        await self.channel_layer.group_send(self.room_group_name, {"type" : "chat.message", "message" : text_data}) #event dictionary, #chat.message corresponds to chat_message
        await self.save_history(text_data)
        msg_history = await self.fetch_history(text_data)
        serialised_data = json.dumps(msg_history) 
        await self.send(serialised_data)           

    @sync_to_async
    def save_history(self, text_data):
       string_text = str(text_data)

       if string_text.startswith("fetch history"):
           return
       
       else:     
        chat_history.objects.create(message=text_data, sender_id=self.channel_name, group_name=self.room_group_name)


    @sync_to_async

    def fetch_history(self, text_data):
        string_text = str(text_data)

        if string_text.startswith("fetch history"):

            numbercrunch = string_text.split()
            number = int(numbercrunch[2])
            msg_objs = chat_history.objects.all()[:number]

            for obj in msg_objs:
                message_history_dict[obj.id] = f" message: {obj.message}, timestamp: {obj.timestamp}"

        return message_history_dict

            
    async def chat_message(self, event):
        await self.send(text_data=event["message"])


        


