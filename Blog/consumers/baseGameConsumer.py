import json, asyncio, random
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from Blog.models import Lobby
from Blog.views.jeux_views import award_game_prize

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
        
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        
        if not hasattr(self, 'group_name'):
            print(self.scope['url_route']['kwargs'])
            self.group_name = f"game_{self.room_name}"
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
        
        print('User', user_id, 'connected to', self.group_name)
        print(self.cache)
        await self.send_json({
            'type': 'print_cache',
            'cache': self.cache
        })

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
                            self.GLOBAL_STATE.pop(self.group_name)
            # Si aucun joueur n'est connecté, lancer le nettoyage après 3 secondes
            if all(not self.cache['players'][player]['connected'] for player in self.cache['players']):
                asyncio.create_task(self.cleanup_room())

    async def cleanup_room(self):
        await asyncio.sleep(3)
        if all(not self.cache['players'][player]['connected'] for player in self.cache['players']):
            if self.GLOBAL_STATE.get(self.group_name):
                self.GLOBAL_STATE.pop(self.group_name)
            # Supprimer le lobby de la DB s'il existe
            await sync_to_async(Lobby.objects.filter(name=self.room_name).delete)()

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type in ['init', 'init_lobby'] and not self.cache['game_state']['started']:
            if self.cache['game_state']['type'] is None:
                self.cache['game_state']['type'] = content.get('game_type')
                self.cache['game_state']['size'] = int(content.get('game_size'))
                self.cache['game_state']['name'] = content.get('game_name')
            content_player = int(content.get('player', None))
            content_team = int(content.get('team', None))
            content_role = content.get('role', None)
            self.cache['players'][content_player] = {'connected': True, 'team': content_team}
            if content_role:
                self.cache['players'][content_player]['role'] = content_role
            self.cache['players'][content_player]['channel'] = self.channel_name
            
            if len(self.cache['players']) == self.cache['game_state']['size'] and all(self.cache['players'][player]['connected'] for player in self.cache['players']):
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'all_players_connected',
                        'message': 'starting game'
                    }
                )
                return

    async def all_players_connected(self, event):
        try:
            await self.send_json({
                'type': 'all_players_connected',
                'message': event['message']
            })
        except Exception as e:
            self.cache['game_task'].cancel()

    async def player_disconnected(self, event):
        try:
            await self.send_json({
                'type': 'player_disconnected',
                'user_id': event['user_id']
            })
        except Exception as e:
            self.cache['game_task'].cancel()
            
    async def award_prize(self, winner_team):
        winners_ids = [player for player in self.cache['players'] if self.cache['players'][player]['team'] == winner_team]
        game_type = self.cache['game_state']['type']
        mise = await sync_to_async(Lobby.objects.filter(name=self.room_name).values_list('mise', flat=True).first)()
        await sync_to_async(award_game_prize)(winners_ids, game_type, mise)
        return