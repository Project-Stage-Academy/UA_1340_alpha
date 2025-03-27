import json
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        self.room = await sync_to_async(Room.objects.filter(id=self.room_id).first)()
        if not self.room:
            self.room = Room(id=self.room_id, participants=[])
            await sync_to_async(self.room.save)()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Connected to the room: {self.room_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Disconnected from the room: {self.room_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message")
        sender_email = data.get("sender")

        if message_text and sender_email:
            try:
                if sender_email not in self.room.participants:
                    self.room.add_participant(sender_email)

                new_message = Message(
                    room=self.room,
                    sender=sender_email,
                    text=message_text,
                    timestamp=datetime.now()
                )
                await sync_to_async(new_message.save)()

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message_text,
                        "sender": sender_email,
                        "timestamp": new_message.timestamp.isoformat(),
                    },
                )
            except Exception as e:
                print(f"Error saving the message: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
        }))
