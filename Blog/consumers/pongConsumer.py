import json, asyncio, random
from Blog.consumers.baseGameConsumer import BaseGameConsumer

class PongConsumer(BaseGameConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store pong-specific state to apply after cache initialization in connect
        self.initial_state = {
            'score': {'team1': 0, 'team2': 0},
            'canvas': {'width': 800, 'height': 500},
            'ball': {'x': 250, 'y': 250, 'vx': random.choice([-5, 5]), 'vy': random.choice([-5, 5])},
            'paddle1': {'y': 200, 'v': 5},
            'paddle2': {'y': 200, 'v': 5}
        }
        self.inputs = {'paddle1': None, 'paddle2': None}

    async def connect(self):
        await super().connect()
        # Initialize inputs in the cache if not already present
        if 'inputs' not in self.cache:
            self.cache['inputs'] = self.inputs
        else:
            self.cache['inputs'].update(self.inputs)
        # Apply pong-specific initial state to the global cache
        self.cache['game_state'].update(self.initial_state)

    async def receive_json(self, content):
        await super().receive_json(content)
        msg_type = content.get('type')
        data = content.get('data', {})
        user_id = self.scope["user"].id

        if msg_type == 'start_game':
            print('User', user_id, 'joined team', self.cache['players'][user_id]['team'])
            await self.send_json({
                'type': 'start_game',
                'game_state': self.cache['game_state']
            })
            if not self.cache['game_task']:
                print('Starting game loop')
                self.cache['game_task'] = asyncio.create_task(self.game_loop())
            self.game_update = asyncio.create_task(self.game_update_loop())
            return            

        elif msg_type == 'key_input':
            key = data.get('key')
            print('User', user_id, 'pressed', key)
            action = data.get('action')
            if key in ['ArrowUp', 'ArrowDown']:
                if self.cache['players'][user_id]['team'] == 1:
                    self.cache['inputs']['paddle1'] = (key, action)
                else:
                    self.cache['inputs']['paddle2'] = (key, action)

        elif msg_type == 'verify_state':
            js_state = data.get('game_state', {})
            # ...existing verification logic...

        elif msg_type == 'test':
            print('Test message received:', self.cache)

    async def game_loop(self):
        try:
            while True:
                bs = self.cache['game_state']['ball']
                paddle1 = self.cache['game_state']['paddle1']
                paddle2 = self.cache['game_state']['paddle2']
                going_right = bs['vx'] > 0

                bs['x'] += bs['vx']
                bs['y'] += bs['vy']
                if bs['y'] <= 6 or bs['y'] >= self.cache['game_state']['canvas']['height']-6:
                    bs['vy'] *= -1

                if bs['y'] >= paddle1['y'] and bs['y'] <= paddle1['y']+100 and bs['x'] <= 36 and not going_right:
                    bs['vx'] *= -1.2
                    bs['vy'] *= 1.2
                    paddle1['v'] *= 1.1
                    paddle2['v'] *= 1.1
                    
                elif bs['y'] >= paddle2['y'] and bs['y'] <= paddle2['y']+100 and bs['x'] >= self.cache['game_state']['canvas']['width']-36 and going_right:
                    bs['vx'] *= -1.2
                    bs['vy'] *= 1.2
                    paddle2['v'] *= 1.1
                    paddle1['v'] *= 1.1

                elif bs['x'] <= 0 or bs['x'] >= self.cache['game_state']['canvas']['width']: # Score
                    if bs['x'] <= 0:
                        self.cache['game_state']['score']['team2'] += 1
                    else:
                        self.cache['game_state']['score']['team1'] += 1
                    bs['x'] = 250
                    bs['y'] = 150
                    bs['vx'] = random.choice([-3, 3])
                    bs['vy'] = random.choice([-3, 3])
                    paddle1['y'] = 100
                    paddle2['y'] = 100
                    paddle1['v'] = 5
                    paddle2['v'] = 5
                    print('Score:', self.cache['game_state']['score'])

                for paddle in ['paddle1', 'paddle2']:
                    inp = self.cache['inputs'].get(paddle)
                    if inp:
                        key, action = inp
                        if action == 'up':
                            self.cache['inputs'][paddle] = None
                        elif action == 'down':
                            self.cache['game_state'][paddle]['y'] += -self.cache['game_state'][paddle]['v'] if key in ['ArrowUp'] else self.cache['game_state'][paddle]['v']

                await asyncio.sleep(1/60) # 30 FPS

        except asyncio.CancelledError:
            print('Game loop cancelled')
            pass

    async def game_update_loop(self):
        try:
            while True:
                await asyncio.create_task(self.send_game_update())
                await asyncio.sleep(1/60)
        except asyncio.CancelledError:
            print('Game update loop cancelled')
            self.game_update.cancel()
        
    async def send_game_update(self):
        await self.send_json({
            'type': 'game_update',
            'game_state': self.cache['game_state']
        })
    
    # async def send_game_update(self):
    #     for player in self.cache['players'].values():
    #         await self.channel_layer.send(
    #             player['channel'],
    #             {
    #                 'type': 'game_update',
    #                 'game_state': self.cache['game_state']
    #             }
    #         )

    # async def game_update(self, event):
    #     try:
    #         await self.send_json({
    #             'type': 'game_update',
    #             'game_state': event['game_state']
    #         })
    #     except Exception as e:
    #         print('Error sending game update:', e)
    #         pass