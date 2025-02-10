import json, asyncio, random
from Blog.consumers.baseGameConsumer import BaseGameConsumer

class PongConsumer(BaseGameConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store pong-specific state to apply after cache initialization in connect
        self.initial_state = {
            'score': {'team1': 0, 'team2': 0},
            'canvas': {'width': 800, 'height': 500},
            'ball': {'x': 250, 'y': 150, 'vx': random.choice([-3, 3]), 'vy': random.choice([-3, 3])},
            'paddle1': {'y': 100},
            'paddle2': {'y': 100}
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
                bs['x'] += bs['vx']
                bs['y'] += bs['vy']
                if bs['y'] <= 5 or bs['y'] >= self.cache['game_state']['canvas']['height']-5:
                    bs['vy'] *= -1
                if bs['x'] <= 5 or bs['x'] >= self.cache['game_state']['canvas']['width']-5:
                    bs['vx'] *= -1

                for paddle in ['paddle1', 'paddle2']:
                    inp = self.cache['inputs'].get(paddle)
                    if inp:
                        key, action = inp
                        if action == 'up':
                            self.cache['inputs'][paddle] = None
                        elif action == 'down':
                            self.cache['game_state'][paddle]['y'] += -5 if key in ['ArrowUp'] else 5

                await self.send_json({
                    'type': 'game_update',
                    'game_state': self.cache['game_state']
                })
                await asyncio.sleep(1/60) # 30 FPS

        except asyncio.CancelledError:
            pass