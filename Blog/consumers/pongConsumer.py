import json, asyncio, random
from Blog.consumers.baseGameConsumer import BaseGameConsumer

class PongConsumer(BaseGameConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state.update({
            'score': {'team1': 0, 'team2': 0},
            'canvas': {'width': 800, 'height': 500},
            'ball': {'x': 250, 'y': 150, 'vx': random.choice([-3, 3]), 'vy': random.choice([-3, 3])},
            'paddle1': {'y': 100},
            'paddle2': {'y': 100}
        })
        self.inputs = {'paddle1': None, 'paddle2': None}

    async def receive_json(self, content):
        super().receive_json(content)
        msg_type = content.get('type')
        data = content.get('data', {})
        user_id = self.scope["user"].id
    
        if msg_type == 'start_game':
            # Initialize game state and start game loop if not already started
            self.players[user_id]['team'] = data.get('team')
            await self.send_json({
                'type': 'start_game',
                'game_state': self.game_state
            })
            if not hasattr(self, 'game_task'):
                self.game_task = asyncio.create_task(self.game_loop())

        elif msg_type == 'key_input':
            # Update paddle movement based on key input
            key = data.get('key')
            action = data.get('action')
            # For simplicity, assume keys "w"/"s" for paddle1 and "ArrowUp"/"ArrowDown" for paddle2
            if key in ['ArrowUp', 'ArrowDown']:
                if self.players[user_id]['team'] == 1:
                    self.inputs['paddle1'] = (key, action)
                else:
                    self.inputs['paddle2'] = (key, action)

        elif msg_type == 'verify_state':
            # Compare received positions with backend state (could log or correct if need be)
            js_state = data.get('game_state', {})
            # ...existing verification logic...

    async def game_loop(self):
        try:
            while True:
                # Update ball position
                bs = self.game_state['ball']
                bs['x'] += bs['vx']
                bs['y'] += bs['vy']
                # Bounce off top/bottom walls
                if bs['y'] <= 0 or bs['y'] >= self.game_state['canvas']['height']:
                    bs['vy'] *= -1
                if bs['x'] <= 0 or bs['x'] >= self.game_state['canvas']['width']:
                    bs['vx'] *= -1

                # Simple paddle collision
                # ...existing collision logic...
                
                # Update paddle positions based on inputs
                for paddle in ['paddle1', 'paddle2']:
                    inp = self.inputs.get(paddle)
                    if inp:
                        key, action = inp
                        if action == 'up':
                            self.inputs[paddle] = None
                        elif action == 'down':
                            self.game_state[paddle]['y'] += -5 if key in ['ArrowUp'] else 5

                # Send update to client
                await self.send_json({
                    'type': 'game_update',
                    'game_state': self.game_state
                })
                # Periodically send a verification signal (could include additional verification data)
                # ...existing verification logic...
                await asyncio.sleep(1/30) # 30 FPS

        except asyncio.CancelledError:
            pass
