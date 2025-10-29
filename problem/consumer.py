import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProblemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.problem_id = self.scope['url_route']['kwargs']['problem_id']
        self.chatspace_uuid = self.scope['url_route']['kwargs']['chatspace_uuid']
        self.room_group_name = f'problem_{self.problem_id}_{self.chatspace_uuid}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return 
        
        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'system_message',
                'message': f"User '{self.user.username}' has joined."
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'system_message',
                    'message': f"User '{self.user.username}' has left."
                }
        )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message' and self.user.is_authenticated:
            message = data.get('message', '')
            if message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': self.user.username
                    }
                )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

    async def system_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': message
        }))