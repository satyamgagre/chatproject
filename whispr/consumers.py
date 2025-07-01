from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify others this user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification',
                'message': f"{self.username} joined the room"
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify others this user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification',
                'message': f"{self.username} left the room"
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'chat_message':
            message = data['message']
            username = data['username']
            room = data['room']

            # Send to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'room': room,
                }
            )

            # Save to DB
            await self.save_message(username, room, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'room': event['room'],
        }))

    async def notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        chat_room = ChatRoom.objects.get(slug=room)
        ChatMessage.objects.create(user=user, room=chat_room, message_content=message)
