import json
from django.shortcuts import render
from ..models import User, GameScore
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from django.utils import timezone
from datetime import timedelta


def record_score(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    data = json.loads(request.body.decode('utf-8'))        
    game = data.get('game')
    score = data.get('score')
    game_score = GameScore(game = game, score = score, user = request.user)
    if game_score != 9999.0:
        game_score.save()
    return JsonResponse({'success' : True})



def get_scores(game_name, time_delta, desc = False):
    '''
    Returns the queryset of the scores of a certain game. 
    game_name : str, name of the game
    order : string, 'desc' si décroissant sinon None
    time_delta : string, deltatime of allowed scores ('daily', 'weekly', 'monthly' or 'all')
    '''
    
    if time_delta == 'all':
        scores = GameScore.objects.filter(game=game_name)

    elif time_delta == 'monthly':
        today = timezone.now().date()
        scores = GameScore.objects.filter(game=game_name, date__year=today.year, date__month=today.month)

    elif time_delta == 'weekly':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        scores = GameScore.objects.filter(game=game_name, date__date__range=(start_of_week, today))

    elif time_delta == 'daily':
        today = timezone.now().date()
        scores = GameScore.objects.filter(game=game_name, date__date=today)


    


    if desc:
        return scores.order_by('-score')
    return scores.order_by('score')


@login_required
def list_jeux(request):
    liste_jeux = [jeu[0] for jeu in settings.JEUX]
    orders = {'Flex' : False,
              'Tracker' : True,
              'Kingboard' : False}

    deltas = ['all', 'monthly', 'weekly', 'daily']

    # Get scores
    data = []

    for jeu in liste_jeux:
        for delta in deltas:
            scores = get_scores(jeu, time_delta = delta, desc = orders[jeu])
            # Get better personal score
            best_score = scores.filter(user=request.user).first()
            print("best score : ", best_score)
            if best_score:
                rg = list(scores).index(best_score) + 1
            else:
                rg = None


            d = {'game' : jeu, 
                 'time_delta' : delta, 
                 'score' : [{'user' : score.user, 'score' : score.score, 'date' : score.date} for score in scores[0:10]],
                 'user_best_score' : {'rg' : rg, 'score' : best_score, 'user' : request.user}}
            data.append(d)

    print(data)

    url = 'Blog/jeux/list_jeux.html'
    
    context = {
        'liste_jeux': liste_jeux,
        'scores' : data,        
    }
    
    return render(request, url, context)

@login_required
def flex(request):

    url = 'Blog/jeux/flex.html'
    
    context = {
        'nom_jeu': 'Flex',        
    }
    
    return render(request, url, context)



@login_required
def tracker(request):

    url = 'Blog/jeux/tracker.html'
    
    context = {
        'nom_jeu': 'Tracker',        
    }
    
    return render(request, url, context)



@login_required
def kingboard(request):

    url = 'Blog/jeux/kingboard.html'
    
    context = {
        'nom_jeu': 'Kingboard',        
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