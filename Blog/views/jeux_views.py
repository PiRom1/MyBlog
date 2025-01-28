import json
from django.shortcuts import render
from ..models import User, GameScore
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json


def record_score(request):
    
    data = json.loads(request.body.decode('utf-8'))        
    game = data.get('game')
    score = data.get('score')
    game_score = GameScore(game = game, score = score, user = request.user)
    game_score.save()
    return JsonResponse({'success' : True})



@login_required
def list_jeux(request):
    liste_jeux = [jeu[0] for jeu in settings.JEUX]

    # Get scores
    scores = {}

    # Get Flex score
    flex_scores = GameScore.objects.filter(game='Flex').order_by('score')[:5]
    scores['Flex'] = [{'user' : flex_score.user, 'score' : flex_score.score} for flex_score in flex_scores]
    



    url = 'Blog/jeux/list_jeux.html'
    
    context = {
        'liste_jeux': liste_jeux,
        'scores' : scores,
        
    }
    
    return render(request, url, context)

@login_required
def flex(request):

    url = 'Blog/jeux/flex.html'
    
    context = {
        'nom_jeu': 'Flex',        
    }
    
    return render(request, url, context)