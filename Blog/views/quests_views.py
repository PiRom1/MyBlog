

from django.shortcuts import render, redirect
from ..models import *
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
import random as rd
import json

def get_data_of_objective(objective_for_quest):
    
    type_objective = objective_for_quest.objectif.type
    sentence = ""

    if type_objective == "hdv":
        sentence = f"Mettre {objective_for_quest.objective_value} objets dans l'Hôtel des Ventes."
        url = "/inventory"
    elif type_objective == "jeu":
        sentence = f"Jouer {objective_for_quest.objective_value} parties dans la salle de jeux."
        url = "/jeux"
    elif type_objective == "enjoy":
        sentence = f"Ajouter {objective_for_quest.objective_value} commentaires dans la timeline Enjoy."
        url = "/enjoy_timeline"
    elif type_objective == "recit":
        sentence = f"Ajouter {objective_for_quest.objective_value} message dans un récit."
        url = "/recits"
    elif type_objective == "soundbox":
        sentence = f"Ajouter {objective_for_quest.objective_value} son dans la soundbox."
        url = "/add_sounds"
    elif type_objective == "pari":
        sentence = f"Créer {objective_for_quest.objective_value} pari."
        url = "/paris/create"
    elif type_objective == "dw_arena":
        sentence = f"Faire {objective_for_quest.objective_value} combat DinoWars en arène."
        url = "/dinowars"


    return {"achieved" : objective_for_quest.achieved,
            "objective_value" : objective_for_quest.objective_value,
            "current_value" : objective_for_quest.current_value,
            "sentence" : sentence,
            "url" : url,
            }



def validate_objective_quest(user, action):

    # Get quest
    quest = Quest.objects.filter(user = user, achieved = False, accepted = True)
    if not quest:  # If no current quest
        return
    
    quest = quest.first()

    # Get objectives
    objectives = ObjectifForQuest.objects.filter(quest = quest)

    for objective in objectives:
        if objective.objectif.type == action and not objective.achieved: # If the action is linked to one of our objectives
            objective.current_value += 1
            objective.achieved = objective.current_value == objective.objective_value
            objective.save()

            print(f"Objectif {objective} mis à jour.")





@login_required()
def quest(request):

    pending_quests = Quest.objects.filter(user = request.user, achieved = False, accepted = False)
    objectives = []
    current_quest = Quest.objects.filter(user = request.user, achieved = False, accepted = True)
    ended = True
    data = []


    if current_quest:  # Si l'utilisateur est en quête
        status = 'is_questing'
        current_quest = current_quest.first()

        objectives_for_quest = ObjectifForQuest.objects.filter(quest = current_quest)

        for objective_for_quest in objectives_for_quest:
            objective_data = get_data_of_objective(objective_for_quest)
            objectives.append(objective_data)
            data.append(objective_data)
            if not objective_for_quest.achieved:
                ended = False
    
        if ended:
            sentence = "Bravo jeune aventurier, vous avez bien mérité cette modeste récompense. Prenez-donc "
            if current_quest.loot_type == "coins":
                sentence += f"ces {current_quest.quantity} diplodocoins !"
            else:
                sentence += "cette lootbox !"
        else:
            sentence = f"Cher aventurier, ajourd'hui vous a été donnée une noble quête. \
                        En récompense, vous obtiendrez {current_quest.quantity} "
            if current_quest.loot_type == "coins":
                sentence += "diplodocoins."
            else:
                sentence += "lootbox."
    
    else: # Si l'utilisateur n'est pas en quête
        ended = False
        if pending_quests: # S'il a des quêtes en attente
            status = 'has_pending_quests'
            for quest in pending_quests:
                data.append({'loot_type' : quest.loot_type, 'quantity' : quest.quantity, 'id' : quest.id})
                sentence = "Cher aventurier, j'ai une tâche cruciale à te proposer. Pourras-tu m'aider ? Bien sûr, tu seras grâcieusement récompensé."
                

        else: # S'il n'a pas de quête en attente (donc s'il a fini ses quêtes quotidiennes)
            status = 'waiting_quests'
            sentence = "Cher aventurier, je n'ai plus de travail à vous offrir aujourd'hui. Revenez demain !"


    

    

    context = {'status' : status,
               'objectives' : objectives,
               'sentence' : sentence,
               'pending_quests' : pending_quests,
               'data' : data,
               'ended' : ended}
    
    return render(request, 'Blog/quests/quests.html', context)



def achieve_quest(request):
    
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    quest = Quest.objects.filter(user = request.user, achieved = False)

    if not quest:
        return JsonResponse({"success" : False, "error" : "L'utilisateur n'a pas de quêtes en cours."})
    
    quest = quest.first()
    quest.achieved = True   

    if quest.loot_type == "coins": # Gagne des pièces
        request.user.coins += quest.quantity
        request.user.save()

    else: # Gagne des boîtes
        for _ in range(quest.quantity):
            box = Item.objects.create(type = "box",
                                    item_id = 1)
            
            UserInventory.objects.create(user = request.user, 
                                        item = box)
    
    quest.save()

            


    return JsonResponse({"success" : True})



def accept_quest(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    data = json.loads(request.body)

    id = data.get('id')

    if not id:
        return JsonResponse({'success' : False, 'error' : "No id provided"})
    
    id = int(id)

    quest = Quest.objects.get(id=id)

    quest.accepted = True

    quest.save()

    Quest.objects.filter(user = request.user, accepted = False, achieved = False).delete()

    return JsonResponse({'success' : True})   
