

from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
import random as rd
from datetime import timedelta

def get_data_of_objective(objective_for_quest):
    
    type_objective = objective_for_quest.objectif.type
    sentence = ""

    if type_objective == "hdv":
        sentence = f"Mettre {objective_for_quest.objective_value} objets dans l'Hôtel des Ventes."
    elif type_objective == "jeu":
        sentence = f"Jouer {objective_for_quest.objective_value} parties dans la salle de jeux."
    elif type_objective == "enjoy":
        sentence = f"Ajouter {objective_for_quest.objective_value} commentaires dans la timeline Enjoy."
    elif type_objective == "recit":
        sentence = f"Ajouter {objective_for_quest.objective_value} message dans un récit."
    elif type_objective == "soundbox":
        sentence = f"Ajouter {objective_for_quest.objective_value} son dans la soundbox."
    elif type_objective == "pari":
        sentence = f"Créer {objective_for_quest.objective_value} pari."


    return {"achieved" : objective_for_quest.achieved,
            "objective_value" : objective_for_quest.objective_value,
            "current_value" : objective_for_quest.current_value,
            "sentence" : sentence
            }



def validate_objective_quest(user, action):

    # Get quest
    quest = Quest.objects.filter(user = user, achieved = False)
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





def generate_quest(user, type : str):

    # Get quantity of loot (1 for box, random nb for coins)
    quantity = 1
    if type == 'coins':
        quantity = round(rd.normalvariate(mu = 150, sigma = 10))

    # Create quest
    quest = Quest.objects.create(user = user,
                                 loot_type = type,
                                 quantity = quantity,
                                 duration = timedelta(days=1))
    
    # Create quest_objectives
    objectives = rd.sample(list(ObjectifQuest.objects.all()), 3)

    for objective in objectives:
        value = rd.randint(objective.n_min, objective.n_max)
        ObjectifForQuest.objects.create(quest = quest, 
                                        objectif = objective,
                                        objective_value = value)
        








@login_required()
def quest(request):

    objectives = []
    has_quest = False
    current_quest = Quest.objects.filter(user = request.user, achieved = False)

    if current_quest:
        current_quest = current_quest.first()
        has_quest = True
        objectives_for_quest = ObjectifForQuest.objects.filter(quest = current_quest)
        achieved = True

        for objective_for_quest in objectives_for_quest:
            objective_data = get_data_of_objective(objective_for_quest)
            objectives.append(objective_data)
            if not objective_for_quest.achieved:
                achieved = False
    
    if achieved:
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

    

    

    context = {'quest' : current_quest,
               'has_quest' : has_quest,
               'objectives' : objectives,
               "sentence" : sentence}
    
    return render(request, 'Blog/quests/quests.html', context)