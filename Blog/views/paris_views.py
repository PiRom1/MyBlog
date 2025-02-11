import json
from django.shortcuts import render
from Blog.models import User, Pari, PariIssue, UserForIssue
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Blog.forms import PariForm
from datetime import timedelta


@login_required
def list_paris(request):

    open_paris = Pari.objects.filter(open=True)
    close_paris = Pari.objects.filter(open=False)


    url = 'Blog/paris/list_paris.html'
    
    context = {'open_paris' : open_paris,
               'close_paris' : close_paris}
    
    return render(request, url, context)


@login_required
def create_pari(request):

    if request.method == 'GET':
    
        url = 'Blog/paris/create_pari.html'

        context = {}

        return render(request, url, context)
    

    if request.method == 'POST':
      
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
        
        data = json.loads(request.body.decode('utf-8'))

        if not data.get('name'):
            return JsonResponse({'success' : False, 'error' : "Le pari n'a pas de nom."})
        
        if len(data.get('issues')) < 2:
            return JsonResponse({'success' : False, 'error' : "Le pari n'a pas assez de choix."})
        
        if not data.get('duration'):
            return JsonResponse({'success' : False, 'error' : "Le pari n'a pas de durée."})
        
        for issue in data.get('issues'):
            if not issue:
                return JsonResponse({'success' : False, 'error' : "Une des issues est vide."})



        try:
            pari = Pari(name = data.get('name'),
                        description = data.get('description'),
                        creator = request.user,
                        duration = timedelta(hours = int(data.get('duration'))),
            )

            pari.save()

            for issue in data.get('issues'):

                pari_issue = PariIssue(pari = pari, 
                                       issue = issue)
                
                pari_issue.save()

            


        
        except Exception as e:
            print(e)
            return JsonResponse({'success' : False, 'error' : ''})
        
        return JsonResponse({'success' : True})