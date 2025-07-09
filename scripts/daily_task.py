from Blog.models import User, Item, UserInventory, Box, Quest, ObjectifForQuest, ObjectifQuest, DWUser, DWUserTeam
from datetime import timedelta, datetime
import random as rd
from Blog.views.utils_views import write_journal_quest_new
from Blog.utils.analyse_chat import chat_score
from constance import config
from django.utils import timezone


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
    
    # Create quest_objectives (exclude if you're already in arena)
    if DWUserTeam.objects.filter(in_arena=True).first().user == user:
        objectives = rd.sample(list(ObjectifQuest.objects.exclude(type='dw_arena')), 3)
    else:
        objectives = rd.sample(list(ObjectifQuest.objects.all()), 3)

    for objective in objectives:
        value = rd.randint(objective.n_min, objective.n_max)
        ObjectifForQuest.objects.create(quest = quest, 
                                        objectif = objective,
                                        objective_value = value)
        


def run():
    
    # # Drop boxes
    # nb_drop = 1
    # nb_coins = 200

    # users = User.objects.all()
    # box_id = Box.objects.last().id
    # for user in users:
    #     user.coins += nb_coins
    #     user.save()
    #     for _ in range(nb_drop):
    #         UserInventory.objects.create(user=user, item=Item.objects.create(type='box', item_id=box_id))

    # print(f'{nb_drop} lootboxes dropped for each user | {nb_coins} coins added to each user')
    delta = timezone.now() - config.last_daily_task_date
    if delta < timedelta(hours=23):  # Si le script a déjà été lancé il y a moins de 23 heures, ne pas éxecuter la suite
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        print(f"Le script a déjà été lancé il y a {hours} heures, {minutes} minutes et {seconds} secondes.")
        return
    
    # Sinon, mettre à jour le champ
    config.last_daily_task_date = timezone.now()

    # generate quests
    for user in User.objects.all():

        quests = Quest.objects.filter(user = user, achieved = False)
        quests.delete()

        generate_quest(user, type = "coins")
        generate_quest(user, type = "lootbox")

        dwuser = DWUser.objects.get(user = user)
        dwuser.arena_energy = 5
        dwuser.save()
    
    write_journal_quest_new()
    print("Quests generated for every user")


    # Chat score
    chat_score()




