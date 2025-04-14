import json
from django.shortcuts import render
from Blog.models import User, Pari, PariIssue, UserForIssue
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Blog.forms import PariForm
from datetime import timedelta
from django.shortcuts import get_object_or_404
from datetime import datetime, timezone
import numpy as np
import json

from Blog.views.quests_views import validate_objective_quest


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
        
        issues = data.get('issues')
        issues = [issue for issue in issues if issue]
        print("issues : ", issues)
        if len(issues) < 2:
            return JsonResponse({'success' : False, 'error' : "Le pari n'a pas assez de choix."})
        
        if not data.get('duration'):
            return JsonResponse({'success' : False, 'error' : "Le pari n'a pas de durée."})
        
        duration = data.get('duration')
        days = 0
        hours = 0
        minutes = 0


        if 'mn' in duration:
            print(duration.split('mn'))
            if duration.split('mn')[-1]:
                return JsonResponse({'success' : False, 'error' : "N'écrivez rien après 'mn'"})
        elif 'h' in duration:
            print(duration.split('h'))
            if duration.split('h')[-1]:
                return JsonResponse({'success' : False, 'error' : "Rajouter 'mn' si vous voulez ajouter des minutes.<br>Sinon laissez vide"})
        elif 'd' in duration:
            print(duration.split('d'))
            if duration.split('d')[-1]:
                return JsonResponse({'success' : False, 'error' : "Rajouter 'h' si vous voulez ajouter des heures.<br>Sinon laissez vide"})



        if len(duration.split('d')) > 1: # if d in duration
            try:
                days = int(duration.split('d')[0])
            except:
                return JsonResponse({'success' : False, 'error' : 'Erreur dans la durée en jours'})
            
            duration = duration.split('d')[-1]
        
        if len(duration.split('h')) > 1: # if d in duration
            try:
                hours = int(duration.split('h')[0])
            except:                
                return JsonResponse({'success' : False, 'error' : 'Erreur dans la durée en heures'})

            duration = duration.split('h')[-1]
        
        if len(duration.split('mn')) > 1: # if d in duration
            try:
                minutes = int(duration.split('mn')[0])
            except:
                return JsonResponse({'success' : False, 'error' : 'Erreur dans la durée en minutes'})
        
        

        try:
            pari = Pari(name = data.get('name'),
                        description = data.get('description'),
                        creator = request.user,
                        duration = timedelta(days = days, hours = hours, minutes = minutes),
            )

            pari.save()

            for issue in issues:

                pari_issue = PariIssue(pari = pari, 
                                       issue = issue)
                
                pari_issue.save()



        except Exception as e:
            print(e)
            return JsonResponse({'success' : False, 'error' : ''})
        
        validate_objective_quest(user = request.user, action = "pari")
        
        return JsonResponse({'success' : True, 'pari_id' : pari.id})



def get_gains(pari):

    
    # Set winning issued
    issues = PariIssue.objects.filter(pari = pari)

    
    mise_totale = 0
    winning_mise_totale = 0
    winning_users = []
    gains = []

    for issue in issues:
        
        users_for_issue = UserForIssue.objects.filter(pari_issue = issue)

        for user_for_issue in users_for_issue:
            mise_totale += user_for_issue.mise
            if issue.winning:
                winning_mise_totale += user_for_issue.mise
                winning_users.append({'user' : user_for_issue.user,
                                      'mise' : user_for_issue.mise})
            else:
                gains.append({'user' : user_for_issue.user,
                              'mise' : -user_for_issue.mise})



    for winning_user in winning_users:
        gain = (winning_user.get('mise') / winning_mise_totale) * mise_totale
        gain = int(gain)
        gains.append({'user' : winning_user.get('user'),
                      'mise' : gain})

    return gains

    


def detail_pari(request, id):

    pari = get_object_or_404(Pari, id=id)
    issues = PariIssue.objects.filter(pari=pari)

    issues_detail = []
    mise_total = 0

    mise_possible = True

    cotes = []
    labels = []
    pie_chart_cotes = []

    for issue in issues:
        user_for_issues = UserForIssue.objects.filter(pari_issue=issue)
    
        issue_detail = []
        somme_totale = 0

        for user_for_issue in user_for_issues:

            somme_totale += user_for_issue.mise

            if user_for_issue.user == request.user:
                mise_possible = False

            issue_detail.append({'user' : user_for_issue.user,
                        'issue' : issue,
                        'mise' : user_for_issue.mise,
                        'comment' : user_for_issue.comment})
            mise_total += user_for_issue.mise

        issues_detail.append({'issue' : issue.issue,
                      'issue_id' : issue.id,
                      'mises' : issue_detail})
        
        cotes.append(somme_totale)
        if somme_totale > 0:
            pie_chart_cotes.append(somme_totale)
            labels.append(issue.issue)
    
    new_cotes = []
    for cote in cotes:
        if cote == 0:
            new_cotes.append(0)
        else:
            new_cotes.append(float(np.round(sum(cotes)/cote, 2)))
    cotes = new_cotes.copy()

    if not pari.open:
        gains = get_gains(pari)
    else:
        gains = None
    
    duree_atteinte = pari.published_date + pari.duration <= datetime.now(timezone.utc) 
        
    is_admin = request.user.is_superuser
    
    url = 'Blog/paris/detail_pari.html'

    print("labels : ", json.dumps(labels))

    context = {'id' : id,
               'pari' : pari,
               'issues' : issues,
               'issues_detail' : issues_detail,
               'mise_totale' : mise_total,
               'mise_possible' : mise_possible,
               'is_admin' : is_admin,
               'gains': gains,
               'cotes' : cotes,
               'labels' : json.dumps(labels),
               'pie_chart_cotes' : pie_chart_cotes,
               'fin_pari' : pari.published_date + pari.duration,
               'duree_atteinte' : duree_atteinte,
               'user' : request.user}
    
    return render(request, url, context)



def parier(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
        
    data = json.loads(request.body.decode('utf-8'))
    
    id_issue = data.get('id_issue')
    mise = data.get('mise')
    commentaire = data.get('commentaire')
    pari_issue = PariIssue.objects.get(id=id_issue)
    # Vérifier que la durée n'est pas écoulée
    if datetime.now(timezone.utc) > pari_issue.pari.published_date + pari_issue.pari.duration:
        return JsonResponse({'success' : False, 'error' : "La durée du paris est écoulée."})


    if not mise:
        return JsonResponse({'success' : False, 'error' : "Veuillez mettre le montant de votre mise."})
    else:
        mise = float(mise)

        if mise <= 0:
            return JsonResponse({'success' : False, 'error' : "Veuillez mettre une mise positive (arnaqueur)."})


    if mise > request.user.coins:
        return JsonResponse({'success' : False, 'error' : "Vous n'avez pas assez d'argent pour miser autant. \nVous êtes un homme ou un animal bon sang ?"})

    UserForIssue.objects.create(user = request.user,
                                pari_issue = PariIssue.objects.get(id=id_issue),
                                mise = mise,
                                comment = commentaire)
    
    request.user.coins -= mise
    request.user.save()


    return JsonResponse({'success' : True})
    

def conclure(request):

    
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
        
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    id_pari = data.get('id_pari')
    winning_issue = int(data.get('winning_issue'))
    print('wining : ', winning_issue)
    pari = Pari.objects.get(id = id_pari)

    # Set winning issued
    issues = PariIssue.objects.filter(pari = pari)

    winning_users = []
    mise_totale = 0
    winning_mise_totale = 0

    print(issues)

    for issue in issues:
        issue.winning = issue.id == winning_issue
        issue.save()

        print(issue.winning)

        users_for_issue = UserForIssue.objects.filter(pari_issue = issue)

        for user_for_issue in users_for_issue:
            print(user_for_issue)
            mise_totale += user_for_issue.mise
            if issue.winning:
                winning_mise_totale += user_for_issue.mise
                winning_users.append({'user_id' : user_for_issue.user.id,
                                      'mise' : user_for_issue.mise})
    
    # Coin repartition

    for winning_user in winning_users:
        gain = (winning_user.get('mise') / winning_mise_totale) * mise_totale
        gain = int(gain)
        user_ = User.objects.get(id = winning_user.get('user_id'))
        user_.coins += gain
        user_.save()

        print(f"{user_.username} a gagné {gain} diplodocoins !")



    print(winning_users, winning_mise_totale)

    

    # Close pari

    pari.open = False
    pari.admin_reviewed = True
    pari.save()


    return JsonResponse({'success' : True})
