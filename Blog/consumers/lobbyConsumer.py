import json
import asyncio  # ...added import...
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
    # Nombre de joueurs requis pour démarrer le jeu (peut être redéfini dans une sous-classe)
    required_players = 2

    # Stockage de l'état de la salle d'attente.
    # Structure : { room_name: { user_id: ready_status, ... } }
    waiting_room = {}

    async def connect(self):
        # Récupérer le nom de la salle d'attente depuis l'URL (si renseigné)
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        safe_room = sanitize_group_name(self.room_name)
        self.group_name = f"waiting_room_{safe_room}"
        
        # Refuser la connexion si l'utilisateur n'est pas authentifié
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        user_id = self.scope["user"].id

        # Initialiser l'état de la salle si nécessaire
        if self.room_name not in WaitingRoomConsumer.waiting_room:
            WaitingRoomConsumer.waiting_room[self.room_name] = {}

        # Ajouter l'utilisateur avec un statut "non prêt" (False)
        WaitingRoomConsumer.waiting_room[self.room_name][user_id] = {'name':self.scope['user'].username,
                                                                     'ready':False}

        # Ajouter le canal au groupe de la salle d'attente
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Informer le groupe qu'un nouveau joueur a rejoint
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "lobby_update",
                "message": f"{self.scope['user'].username} a rejoint la salle d'attente",
                "waiting": WaitingRoomConsumer.waiting_room[self.room_name],
            }
        )

    async def disconnect(self, close_code):
        user_id = self.scope["user"].id
        # Supprimer l'utilisateur de la salle d'attente
        if self.room_name in WaitingRoomConsumer.waiting_room:
            WaitingRoomConsumer.waiting_room[self.room_name].pop(user_id, None)
        
        # Retirer le canal du groupe
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        # Informer le groupe qu'un joueur a quitté
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "lobby_update",
                "message": f"{self.scope['user'].username} a quitté la salle d'attente",
                "waiting": WaitingRoomConsumer.waiting_room.get(self.room_name, {}),
            }
        )
        
        # Si aucun joueur n'est connecté, lancer le nettoyage après 5 secondes
        if not WaitingRoomConsumer.waiting_room.get(self.room_name):
            asyncio.create_task(self.cleanup_room())

    async def cleanup_room(self):
        await asyncio.sleep(3)
        # Re-vérifier si la salle est toujours vide
        if not WaitingRoomConsumer.waiting_room.get(self.room_name):
            # Supprimer la salle du cache en mémoire
            WaitingRoomConsumer.waiting_room.pop(self.room_name, None)
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

        if action in ["join", "create"]:
            # Initialiser la salle si nécessaire
            if self.room_name not in WaitingRoomConsumer.waiting_room:
                WaitingRoomConsumer.waiting_room[self.room_name] = {}
            # Ajouter l'utilisateur s'il n'est pas déjà présent
            WaitingRoomConsumer.waiting_room[self.room_name][user_id] = {'name':self.scope['user'].username,
                                                                     'ready':False}

            # Envoyer au joueur ses infos de connexion
            await self.send_json({
                "type": "connection_info",
                "user": {
                    "id": self.scope["user"].id,
                    "username": self.scope["user"].username,
                }
            })

            # Notifier le groupe
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} a rejoint le lobby",
                    "waiting": WaitingRoomConsumer.waiting_room[self.room_name],
                }
            )

        elif action == "ready":
            # Mettre à jour le statut de l'utilisateur à "prêt"
            if self.room_name in WaitingRoomConsumer.waiting_room:
                WaitingRoomConsumer.waiting_room[self.room_name][user_id]['ready'] = True

            # Informer le groupe de ce changement
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} est prêt",
                    "waiting": WaitingRoomConsumer.waiting_room[self.room_name],
                }
            )

            # Vérifier si le nombre de joueurs est suffisant et si tous sont prêts
            current_players = WaitingRoomConsumer.waiting_room[self.room_name]
            if len(current_players) >= self.required_players and all(current_players.values()):
                # Tous les joueurs sont prêts : notifier le groupe
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "start_game",
                        "message": "Tous les joueurs sont prêts. Le jeu va démarrer !",
                    }
                )

        elif action == "not_ready":
            # L'utilisateur annule son statut "prêt"
            if self.room_name in WaitingRoomConsumer.waiting_room:
                WaitingRoomConsumer.waiting_room[self.room_name][user_id]['ready'] = False

            # Informer le groupe
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "lobby_update",
                    "message": f"{self.scope['user'].username} n'est plus prêt",
                    "waiting": WaitingRoomConsumer.waiting_room[self.room_name],
                }
            )

    async def lobby_update(self, event):
        """
        Méthode appelée pour diffuser une mise à jour de la salle d'attente à tous les clients.
        """
        await self.send_json({
            "type": "lobby_update",
            "message": event["message"],
            "waiting": event["waiting"],
        })

    async def start_game(self, event):
        """
        Méthode appelée lorsque tous les joueurs sont prêts et que le jeu doit démarrer.
        """
        await self.send_json({
            "type": "start_game",
            "message": event["message"],
        })
