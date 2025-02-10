import json, asyncio, random
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class BaseGameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from Blog.cache import GLOBAL_STATE
        self.GLOBAL_STATE = GLOBAL_STATE

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            print('User not authenticated')
            await self.close()
            return
        user_id = self.scope["user"].id
        await self.accept()
        
        if not hasattr(self, 'group_name'):
            print(self.scope['url_route']['kwargs'])
            room_name = self.scope['url_route']['kwargs'].get('room_name')
            self.group_name = f"game_{room_name}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            if self.group_name not in self.GLOBAL_STATE:
                self.GLOBAL_STATE[self.group_name] = {
                    'players': {},
                    'waiting_to_reconnect': [],
                    'game_state': {
                        'name': None,
                        'size': None,
                        'type': None,
                        'started': False,
                        'finished': False,
                    },
                    'game_task': None
                }
            self.cache = self.GLOBAL_STATE[self.group_name]

        if user_id in self.cache['players']:
            self.cache['players'][user_id]['connected'] = True
            if not self.cache['game_state']['started']:
                if len(self.cache['players']) == self.cache['game_state']['size'] and all(self.cache['players'][player]['connected'] for player in self.cache['players']):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'all_players_connected',
                            'message': 'starting game'
                        }
                    )
            else:
                self.cache['waiting_to_reconnect'].remove(user_id)
                if all(self.cache['players'][player]['connected'] for player in self.cache['players']):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'all_players_connected',
                            'message': 'unpause game'
                        }
                    )
                    await asyncio.sleep(3)
                    self.cache['game_task'].uncancel() 

    async def disconnect(self, close_code):
        user_id = self.scope["user"].id
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            if user_id in self.cache['players']:
                self.cache['players'][user_id]['connected'] = False
                if self.cache['game_state']['started']:
                    if not self.cache['game_state']['finished']:
                        if hasattr(self, 'game_task'):
                            self.cache['game_task'].cancel()
                        self.cache['waiting_to_reconnect'].append(user_id)
                        await self.channel_layer.group_send(
                            self.group_name,
                            {
                                'type': 'player_disconnected',
                                'user_id': user_id
                            }
                        )
                    else:
                        self.cache['players'].pop(user_id)
                        if not self.cache['players']:
                            await self.close()

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type in ['init', 'init_lobby'] and not self.cache['game_state']['started']:
            if self.cache['game_state']['type'] is None:
                self.cache['game_state']['type'] = content.get('game_type')
                self.cache['game_state']['size'] = content.get('game_size')
                self.cache['game_state']['name'] = content.get('game_name')
            content_player = content.get('player', None)
            content_team = content.get('team', None)
            content_role = content.get('role', None)
            self.cache['players'][content_player] = {'connected': True, 'team': content_team}
            if content_role:
                self.cache['players'][content_player]['role'] = content_role

            if len(self.cache['players']) == self.cache['game_state']['size'] and all(self.cache['players'][player]['connected'] for player in self.cache['players']):
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'all_players_connected',
                        'message': 'starting game'
                    }
                )

    async def all_players_connected(self, event):
        await self.send_json({
            'type': 'all_players_connected',
            'message': event['message']
        })

    async def init_lobby(self, event):
        print('Init lobby:', event)
        content_player = event.get('player')
        content_team = event.get('team')
        content_role = event.get('role')
        if not self.cache['game_state']['started']:
            if self.cache['game_state']['type'] is None:
                self.cache['game_state']['type'] = event.get('game_type')
                self.cache['game_state']['size'] = event.get('game_size')
                self.cache['game_state']['name'] = event.get('game_name')
            self.cache['players'][content_player] = {'connected': True, 'team': content_team}
            if content_role:
                self.cache['players'][content_player]['role'] = content_role
            if len(self.cache['players']) == self.cache['game_state']['size'] and all(self.cache['players'][player]['connected'] for player in self.cache['players']):
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'all_players_connected',
                        'message': 'starting game'
                    }
                )