# monjeu/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Pour l'exemple, on stocke l'état du jeu dans une variable globale.
# ATTENTION : Cette solution n'est pas recommandée en production.
GAME_STATE = {
    'score': 0,  # score neutre; positif => avantage joueur 1, négatif => avantage joueur 2
    'threshold': 5,  # seuil pour déclarer un gagnant
}

class TugOfWarConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'tugofwar_game'
        # Ajoute le canal à la room.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Envoyer l'état initial du jeu à ce nouveau joueur.
        await self.send_json({
            'type': 'init',
            'score': GAME_STATE['score']
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        """
        Attendre un message JSON du client.
        On attend par exemple :
            {
                "action": "pull",
                "player": "player1"  # ou "player2"
            }
        """
        action = content.get('action')
        if action == 'pull':
            player = content.get('player')
            # Met à jour l'état du jeu
            if player == 'player1':
                GAME_STATE['score'] += 1
            elif player == 'player2':
                GAME_STATE['score'] -= 1

            # Vérifier si un joueur a gagné
            winner = None
            if GAME_STATE['score'] >= GAME_STATE['threshold']:
                winner = 'player1'
            elif GAME_STATE['score'] <= -GAME_STATE['threshold']:
                winner = 'player2'

            # Diffuser l'état mis à jour à tous les joueurs
            message = {
                'type': 'game_update',
                'score': GAME_STATE['score'],
                'last_player': player,
                'winner': winner
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                message
            )

            # Si le jeu est terminé, on peut réinitialiser l'état ou gérer la fin autrement.
            if winner:
                # Par exemple, on réinitialise après une victoire.
                GAME_STATE['score'] = 0

    async def game_update(self, event):
        """
        Méthode appelée lorsque le message 'game_update' est envoyé à la room.
        """
        await self.send_json({
            'score': event['score'],
            'last_player': event['last_player'],
            'winner': event.get('winner')
        })
