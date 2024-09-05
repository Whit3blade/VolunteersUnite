import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        # Accept  connetion
        await self.accept()
        # Get / create ChatRoom
        room, created = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)
        # Fetch previous messages in a separate synchronous function
        messages = await self.get_previous_messages(room)
        messages_data = await self.format_messages(messages)  # Ensure this method exists
        # Send previous messages to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages_data
        }))
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    @database_sync_to_async
    def get_previous_messages(self, room):
        return list(ChatMessage.objects.filter(room=room).order_by('timestamp'))

    async def format_messages(self, messages):
        # Format the message asynchronously
        messages_data = []
        for message in messages:
            # Fetch the username in an async-safe way
            username = await database_sync_to_async(lambda: message.sender.username)()
            messages_data.append({
                'username': username,
                'message': message.message,
                'timestamp': message.timestamp.isoformat()
            })
        return messages_data

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        timestamp = text_data_json['timestamp']

        # Save message to the database
        room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)
        sender = await database_sync_to_async(User.objects.get)(username=username)
        await database_sync_to_async(ChatMessage.objects.create)(room=room, sender=sender, message=message)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
            'timestamp': timestamp
        }))
