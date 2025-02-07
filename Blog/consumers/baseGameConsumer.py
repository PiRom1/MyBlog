import json, asyncio, random
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class BaseGameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = {}  # store allowed players, their connection status, and their game info
        # Structure: { user_id: { 'connected': True/False, 'team': 1/2 } }
        self.waiting_to_reconnect = []  # store user_ids waiting to reconnect
        self.game_state = {
            'name': None,
            'size': None,
            'type': None,
            'started': False,
            'finished': False,
        }
        self.game_task = None

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        user_id = self.scope["user"].id
        await self.accept()
        
        if not hasattr(self, 'group_name'):
            print(self.scope['url_route']['kwargs'])
            room_name = self.scope['url_route']['kwargs'].get('room_name')
            self.group_name = f"game_{room_name}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            return

        if user_id in self.players:
            self.players[user_id]['connected'] = True
            if not self.game_state['started']:
                if len(self.players) == self.game_state['size'] and all(self.players[player]['connected'] for player in self.players):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'all_players_connected',
                            'message': 'starting game'
                        }
                    )
            else:
                self.waiting_to_reconnect.remove(user_id)
                if all(self.players[player]['connected'] for player in self.players):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'all_players_connected',
                            'message': 'unpause game'
                        }
                    )
                    await asyncio.sleep(3)
                    self.game_task.uncancel() 

        else:
            await self.close(4001, 'Unauthorized')

    async def disconnect(self, close_code):
        user_id = self.scope["user"].id
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            if user_id in self.players:
                self.players[user_id]['connected'] = False
                if self.game_state['started']:
                    if not self.game_state['finished']:
                        if hasattr(self, 'game_task'):
                            self.game_task.cancel()
                        self.waiting_to_reconnect.append(user_id)
                        await self.channel_layer.group_send(
                            self.group_name,
                            {
                                'type': 'player_disconnected',
                                'user_id': user_id
                            }
                        )
                    else:
                        self.players.pop(user_id)
                        if not self.players:
                            await self.close()
        # print who disconnected if it isn't a player
        print(self.scope)

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type == 'init' and not self.game_state['started']:
            if self.game_state['type'] is None:
                self.game_state['type'] = content.get('game_type')
                self.game_state['size'] = content.get('game_size')
                self.game_state['name'] = content.get('game_name')
            content_player = content.get('player', None)
            content_team = content.get('team', None)
            content_role = content.get('role', None)
            self.players[content_player] = {'connected': True, 'team': content_team}
            if content_role:
                self.players[content_player]['role'] = content_role

            # Verify all players are connected before starting game
            if not self.game_state['started']:
                if len(self.players) == self.game_state['size'] and all(self.players[player]['connected'] for player in self.players):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'all_players_connected',
                            'message': 'starting game'
                        }
                    )

    async def all_players_connected(self, event):
        # Send start signal to all players
        await self.send_json({
            'type': 'all_players_connected',
            'message': event['message']
        })