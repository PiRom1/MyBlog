from Blog.models import User, Item, UserInventory, Box, Quest, ObjectifForQuest, ObjectifQuest, DWUser, DWUserTeam, DWFight, DWPvmRun, DWPvmNewRun, DWPvmDino
from datetime import timedelta, datetime
from constance import config as constance_cfg
import random as rd
from Blog.views.utils_views import write_journal_quest_new
from Blog.utils.analyse_chat import chat_score
from constance import config
from django.utils import timezone
from django.db import transaction


def generate_quest(user, type : str):

    try:
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
    except Exception as e:
        raise SystemError(f"Erreur lors de la génération des quêtes : {e}")
    

def reset_pvm_runs_td():
    for dwuser in DWUser.objects.all():
        dwuser.pvm_runs_td = 0
        dwuser.save()
        user = dwuser.user
        run = DWPvmRun.objects.filter(user = user)
        if run.exists():
            run = run.first()
            if run.level == 1:
                run.delete()
                DWPvmNewRun.objects.filter(user=user).delete()
                DWPvmDino.objects.filter(user=user).delete()

def clear_fights_log():
    for fight in DWFight.objects.filter(gamemode = 'arena', date__lt = timezone.now() - timedelta(days=30)):
        fight.delete()
    for fight in DWFight.objects.filter(gamemode = 'pvm', date__lt = timezone.now() - timedelta(days=2)):
        fight.delete()
    for fight in DWFight.objects.filter(gamemode = 'duel', date__lt = timezone.now() - timedelta(days=1)):
        fight.delete()


@transaction.atomic
def run():
    
    now = timezone.now()
    delta = now - config.last_daily_task_date
    if delta < timedelta(hours=23):  # Si le script a déjà été lancé il y a moins de 23 heures, ne pas éxecuter la suite
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        print(f"Le script a déjà été lancé il y a {hours} heures, {minutes} minutes et {seconds} secondes.")
        return
    
    try:

        # generate quests
        for user in User.objects.all():

            quests = Quest.objects.filter(user = user, achieved = False)
            quests.delete()

            generate_quest(user, type = "coins")
            generate_quest(user, type = "lootbox")

            try:
                dwuser, created = DWUser.objects.get_or_create(user = user)
                dwuser.arena_energy = 5
                if created: # Si l'utilisater a été créé, lui donner des oeufs gratuits
                    dwuser.free_hatch = 50
                    print(f"Création de l'utilisateur DinoWars {user}")

                dwuser.save()
            except Exception as e:
                raise SystemError(f"Erreur lors de la réinitialisation de l'énergie d'arène : {e}")
        
        try:
            write_journal_quest_new()
            print("Quests generated for every user")
        except Exception as e:
            raise SystemError(f"Erreur lors de l'écriture en journal des quêtes : {e}")

        try:
            # Chat score
            chat_score()
        except Exception as e:
            raise SystemError(f"Erreur lors du calcul des scores de chat : {e}")

        try:
            # Clear fights log
            clear_fights_log()
        except Exception as e:
            raise SystemError(f"Erreur lors de l'effaçage des logs de combat DW : {e}")

        try:
            reset_pvm_runs_td()
        except Exception as e:
            raise SystemError(f"Erreur lors de la réinitialisation du PVM DW : {e}")
        
        # Si tout s'est bien passé, fin du script et actualisation de l'heure
        config.last_daily_task_date = now

    
    except Exception as e:
        transaction.set_rollback(True) # Annuler les imputations s'il y a eu une erreur
        print(e)



