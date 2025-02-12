import json
from django.shortcuts import render
from ..models import User, GameScore, Lobby, Game
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging


def record_score(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    data = json.loads(request.body.decode('utf-8')) 
    print(data)       
    game = Game.objects.get(name=data.get('game'))
    score = data.get('score')
    game_score = GameScore(game = game, score = score, user = request.user)
    game_score.save()
    return JsonResponse({'success' : True})



def get_scores(game, time_delta, desc = False):
    '''
    Returns the queryset of the scores of a certain game. 
    game_name : str, name of the game
    order : string, 'desc' si décroissant sinon None
    time_delta : string, deltatime of allowed scores ('daily', 'weekly', 'monthly' or 'all')
    '''
    
    if time_delta == 'all':
        scores = GameScore.objects.filter(game=game)

    elif time_delta == 'monthly':
        today = timezone.now().date()
        scores = GameScore.objects.filter(game=game, date__year=today.year, date__month=today.month)

    elif time_delta == 'weekly':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        scores = GameScore.objects.filter(game=game, date__date__range=(start_of_week, today))

    elif time_delta == 'daily':
        today = timezone.now().date()
        scores = GameScore.objects.filter(game=game, date__date=today)

    if desc:
        return scores.order_by('-score')
    return scores.order_by('score')


@login_required
def list_jeux(request):
    liste_jeux_solo = Game.objects.filter(gameType='solo')
    liste_jeux_multi = Game.objects.exclude(gameType='solo')

    deltas = ['all', 'monthly', 'weekly', 'daily']

    # Get scores
    data = []

    for jeu in liste_jeux_solo:
        if jeu.score != -1:
            for delta in deltas:
                scores = get_scores(jeu.id, time_delta = delta, desc = jeu.score)
                # Get better personal score
                best_score = scores.filter(user=request.user).first()
                if best_score:
                    rg = list(scores).index(best_score) + 1
                else:
                    rg = None


                d = {'game' : jeu.name, 
                    'time_delta' : delta, 
                    'score' : [{'user' : score.user, 'score' : score.score, 'date' : score.date} for score in scores[0:10]],
                    'user_best_score' : {'rg' : rg, 'score' : best_score, 'user' : request.user}}
                data.append(d)

    url = 'Blog/jeux/list_jeux.html'
    
    context = {
        'liste_jeux_solo': liste_jeux_solo,
        'liste_jeux_multi': liste_jeux_multi,
        'scores' : data,        
        'user' : request.user.id
    }
    
    return render(request, url, context)

@login_required
def play_game(request, game):

    url = f'Blog/jeux/{game}.html'
    
    context = {
        'nom_jeu': game,        
    }
    
    return render(request, url, context)


@login_required
def stats(request):

    url = 'Blog/jeux/stats.html'

    scores = list(GameScore.objects.filter(game='Kingboard', user=request.user).values_list('score', flat=True))
    data = [{"y" : scores,
            "x" : [i for i in range(0, len(scores))],
            "line" : {"color" : "white"}},
            {"margin": { "t": 0 },
             "type" : "scatter"},
        ]


    context = {'data' : data}

    return render(request, url, context)

def get_game_size(game_type):
    if game_type == 'solo':
        return 1
    elif game_type == '1v1':
        return 2
    else:
        return 4

@login_required
def lobby_page(request, room_name):
    try:
        lobby = Lobby.objects.get(name=room_name)
    except Lobby.DoesNotExist:
        return HttpResponseRedirect('/jeux/')
    game_name = lobby.game.name
    game_type = lobby.game.gameType
    game_size = get_game_size(game_type)
    return render(request, 'Blog/jeux/lobby.html', {'room_name': room_name,
                                                    'game_name': game_name,
                                                    'game_size': game_size,
                                                    'game_type': game_type})

# New view to fetch open lobbies dynamically.
@login_required
def get_open_lobbies(request):
    # Query open lobbies from the database
    lobbies = Lobby.objects.all()
    lobby_list = []
    for lobby in lobbies:
        lobby_list.append({
            'name': lobby.name,
            'game': lobby.game.name,
            'size': get_game_size(lobby.game.gameType),
        })
    return JsonResponse({'lobbies': lobby_list})

logger = logging.getLogger(__name__)

@login_required
def create_lobby(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"JSON reçu: {data}")
        lobby_name = data.get('lobby')
        game = Game.objects.get(name=data.get('game'))
        if Lobby.objects.filter(name=lobby_name).exists():
            return JsonResponse({'success': False, 'error': 'Lobby already exists'})
        Lobby.objects.create(name=lobby_name, game=game)
        print(f'Lobby {lobby_name} created for game {game}')
        return JsonResponse({'success': True})
    print('Invalid request method')
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def play_lobby_game(request, token):
    if request.method == "POST":
        room_name = request.POST.get('roomName')
        player_team = request.POST.get('team')
        player_role = request.POST.get('role')
    player_id = request.user.id
    try:
        lobby = Lobby.objects.get(name=room_name)
    except Lobby.DoesNotExist:
        return render(request, f'Blog/jeux/{game_name}.html', {'room_name': room_name})
    
    game_name = lobby.game.name
    game_type = lobby.game.gameType
    game_size = get_game_size(game_type)
    if token == lobby.token:
        print(f"User authenticated: {request.user.is_authenticated}")
        # Remove sending init_lobby here to ensure the consumer is initialized
        # Instead, pass required info to the template so that client code sends init_lobby after websocket connection is open.
        context = {
            'room_name': room_name,
            'game_name': game_name,
            'game_size': game_size,
            'game_type': game_type,
            'player': player_id,
            'team': player_team,
            'role': player_role
        }
        return render(request, f'Blog/jeux/{game_name}.html', context)
    else:
        return HttpResponseRedirect('/jeux/')

