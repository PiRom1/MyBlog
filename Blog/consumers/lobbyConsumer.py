import json
import asyncio
import random
import string  # ...added import...
from asgiref.sync import sync_to_async  # ...added for Django ORM calls...
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from Blog.models import Lobby  # ...added import for DB deletion
import re  # added import for sanitization

def sanitize_group_name(name):
    # Allow only ASCII alphanumerics, hyphens, underscores, and periods.
    valid = re.sub(r'[^A-Za-z0-9\-\_\.]', '', name)
    # Ensure length is less than 100 chars.
    return valid[:99]

class WaitingRoomConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer réutilisable pour gérer une salle d'attente de joueurs.
    
    Les joueurs authentifiés rejoignent la salle et indiquent leur disponibilité
    en envoyant l'action "ready". Lorsque le nombre requis de joueurs est présent
    et que tous sont prêts, le consumer envoie un message indiquant que le jeu peut démarrer.
    
    Pour utiliser ce consumer pour un jeu particulier, vous pouvez hériter de cette classe
    et éventuellement redéfinir le nombre de joueurs requis.
    """

    # Stockage de l'état de la salle d'attente.
    # Structure : { room_name: { players: { user_id: {name, ready, team, role, channel} }, game, size, type } }
    waiting_room = {}

    async def connect(self):
        # Récupérer le nom de la salle d'attente depuis l'URL (si renseigné)
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        self.game_name = self.scope['url_route']['kwargs'].get('game', 'default')
        self.game_size = int(self.scope['url_route']['kwargs'].get('size', 2))
        self.game_type = self.scope['url_route']['kwargs'].get('type', 'default')
        safe_room = sanitize_group_name(self.room_name)
        self.group_name = f"waiting_room_{safe_room}"
        
        # Refuser la connexion si l'utilisateur n'est pas authentifié
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        user_id = self.scope["user"].id
        # get state value from lobby database
        state = await sync_to_async(Lobby.objects.filter(name=self.room_name).values_list('state', flat=True).first)()
        print(state)

        # Initialiser l'état de la salle si nécessaire
        if self.room_name not in WaitingRoomConsumer.waiting_room:
            if state == 'waiting':
                WaitingRoomConsumer.waiting_room[self.room_name] = {'players': {}, 'game': self.game_name, 'size': self.game_size, 'type': self.game_type}
            else:
                await self.accept()
                await self.send_json({"type": "game_started", "message": "Le jeu a déjà démarré."})
                await self.close(code=4001)
                return

        # Refuser la connexion si la salle d'attente est pleine
        elif len(WaitingRoomConsumer.waiting_room[self.room_name]['players']) >= WaitingRoomConsumer.waiting_room[self.room_name]['size']:
                await self.accept()
                await self.send_json({"type": "room_full", "message": "La salle est pleine."})
                await self.close(code=4001)
                return

        # Ajouter l'utilisateur avec un statut "non prêt" (False)
        WaitingRoomConsumer.waiting_room[self.room_name]['players'][user_id] = {'name':self.scope['user'].username,
                                                                     'ready':False, 'team':None, 'role':None, 'channel':self.channel_name}

        # Ajouter le canal au groupe de la salle d'attente
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Informer le groupe qu'un nouveau joueur a rejoint
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "lobby_update",
                "message": f"{self.scope['user'].username} a rejoint la salle d'attente",
                "players": WaitingRoomConsumer.waiting_room[self.room_name]['players'],
            }
        )

    async def disconnect(self, close_code):
        user_id = self.scope["user"].id
        # Retirer le canal du groupe
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # Supprimer l'utilisateur de la salle d'attente
        if self.room_name in WaitingRoomConsumer.waiting_room:
            WaitingRoomConsumer.waiting_room[self.room_name]['players'].pop(user_id, None)
         
            # Informer le groupe qu'un joueur a quitté
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} a quitté la salle d'attente",
                    "players": WaitingRoomConsumer.waiting_room[self.room_name]['players'],
                }
            )
        
        # Si aucun joueur n'est connecté, lancer le nettoyage après 5 secondes
        if len(WaitingRoomConsumer.waiting_room[self.room_name]['players']) == 0:
            asyncio.create_task(self.cleanup_room())

    async def cleanup_room(self):
        await asyncio.sleep(3)
        # Re-vérifier si la salle est toujours vide
        if self.room_name in WaitingRoomConsumer.waiting_room and len(WaitingRoomConsumer.waiting_room[self.room_name]['players']) == 0:
            # Supprimer la salle du cache en mémoire
            WaitingRoomConsumer.waiting_room.pop(self.room_name, None)

        if await sync_to_async(Lobby.objects.filter(name=self.room_name).values_list('state', flat=True).first)() == 'waiting':
            # Supprimer le lobby de la DB s'il existe
            await sync_to_async(Lobby.objects.filter(name=self.room_name).delete)()

    async def receive_json(self, content):
        """
        Le consumer attend des messages JSON contenant une action.
        
        - "ready" : le joueur indique qu'il est prêt.
        - "not_ready" : le joueur annule son statut prêt.
        """
        action = content.get("action")
        user_id = self.scope["user"].id

        if action == "ready":
            # Mettre à jour le statut de l'utilisateur à "prêt"
            if self.room_name in WaitingRoomConsumer.waiting_room:
                WaitingRoomConsumer.waiting_room[self.room_name]['players'][user_id]['ready'] = True

            # Informer le groupe de ce changement
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} est prêt",
                    "players": WaitingRoomConsumer.waiting_room[self.room_name]['players'],
                }
            )

            # Vérifier si le nombre de joueurs est suffisant et si tous sont prêts
            current_players = WaitingRoomConsumer.waiting_room[self.room_name]['players']
            required_players = WaitingRoomConsumer.waiting_room[self.room_name]['size']
            if len(current_players) >= required_players and all(cp['ready'] for cp in current_players.values()):
                # Tous les joueurs sont prêts : notifier le groupe
                # await self.send_json({
                #     "type": "all_ready",
                #     "message": "Tous les joueurs sont prêts. Le jeu va démarrer !",
                # })
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "all_ready",
                        "message": "Tous les joueurs sont prêts. Le jeu va démarrer !",
                    }
                )
                asyncio.create_task(self.game_start())
                
        elif action == "not_ready":
            # L'utilisateur annule son statut "prêt"
            if self.room_name in WaitingRoomConsumer.waiting_room:
                WaitingRoomConsumer.waiting_room[self.room_name]['players'][user_id]['ready'] = False

            # Informer le groupe
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} n'est plus prêt",
                    "players": WaitingRoomConsumer.waiting_room[self.room_name]['players'],
                }
            )

    async def lobby_update(self, event):
        """
        Méthode appelée pour diffuser une mise à jour de la salle d'attente à tous les clients.
        """
        await self.send_json({
            "type": "lobby_update",
            "message": event["message"],
            "players": event["players"],
        })

    async def all_ready(self, event):
        """
        Méthode appelée lorsque tous les joueurs sont prêts.
        """
        await self.send_json({
            "type": "all_ready",
            "message": event["message"],
        })

    async def start_game(self, event):
        """
        Méthode appelée pour rediriger les joueurs vers le jeu.
        """
        await self.send_json({
            "type": "start_game",
            "message": event["message"],
            "token": event["token"],
            "team": event["team"],
            "role": event["role"],
        })

    async def assign_teams(self):
        """
        Méthode pour attribuer des équipes et rôles aux joueurs. Aléatoire pour l'instant.
        """
        game_type = WaitingRoomConsumer.waiting_room[self.room_name]['type']
        players = list(WaitingRoomConsumer.waiting_room[self.room_name]['players'].keys())
        random.shuffle(players)
        if game_type == '1v1':
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[0]]['team'] = 1
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[1]]['team'] = 2
        elif game_type == '2v2':
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[0]].update({'team': 1, 'role': 1})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[1]].update({'team': 1, 'role': 2})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[2]].update({'team': 2, 'role': 1})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[3]].update({'team': 2, 'role': 2})

        elif game_type == '3v1':
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[0]].update({'team': 1, 'role': 1})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[1]].update({'team': 1, 'role': 2})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[2]].update({'team': 1, 'role': 3})
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[3]].update({'team': 2, 'role': 4})
        else:
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[0]]['team'] = 1
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[1]]['team'] = 2
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[2]]['team'] = 3
            WaitingRoomConsumer.waiting_room[self.room_name]['players'][players[3]]['team'] = 4
        return

    async def game_start(self):
        """
        Méthode appelée pour démarrer le jeu.
        """
        # Attendre 3 secondes avant de rediriger les joueurs vers le jeu
        await asyncio.sleep(3)
        # Re-vérifier si le nombre de joueurs est suffisant et si tous sont prêts
        current_players = WaitingRoomConsumer.waiting_room[self.room_name]['players']
        required_players = WaitingRoomConsumer.waiting_room[self.room_name]['size']
        if len(current_players) >= required_players and all(cp['ready'] for cp in current_players.values()):
            # Générer un token unique pour la salle d'attente de 16 caractères
            token = self.room_name+'_'+''.join(random.choices(string.ascii_letters + string.digits, k=16))
            # Enregistrer le token dans la base de données
            await sync_to_async(Lobby.objects.filter(name=self.room_name).update)(token=token)
            # Modifier l'attribut "state" du lobby dans la base de données
            await sync_to_async(Lobby.objects.filter(name=self.room_name).update)(state='playing')      
            # Attribuer des équipes et rôles aux joueurs
            await self.assign_teams()
            for player in current_players.values():
                # Envoyer un message de démarrage à chaque joueur
                await self.channel_layer.send(
                    player['channel'],
                    {
                        "type": "start_game",
                        "message": "Redirection vers le jeu...",
                        "token": token,
                        "team": player['team'],
                        "role": player['role'],
                    }
                )
