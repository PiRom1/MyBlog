from Blog.models import User, Item, UserInventory, SessionUser, DWUser, Session, Quest, ObjectifForQuest, ObjectifQuest
from django.db import transaction
from datetime import timedelta
import random as rd

## Create a new user and : 
##  - Associates him to new sessions
##  - Gives him a system user prompt for bot answers
##  - Gives him diplodocoins and lootboxes
##  - Gives him a DinoWars user
##  - Generates him two quests


DEFAULT_COINS = 5000
DEFAULT_BOXES = 20
DW_FREE_HATCH = 100


def create_user():

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📝 Informations utilisateur")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    username = input("  Username : ")
    password = input("  Password : ")
    prenom = input("  Prénom : ")
    nom = input("  Nom : ")
    email = input("  Email (laissez vide si inconnue) : ")
    print()
    system_prompt = input("  Une description amusante de cette personne\n  (pour que les bots lui répondent de façon fun et ciblée !)\n  → ")

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=prenom,
        last_name=nom,
        email=email,
        llm_context=system_prompt,
        coins=DEFAULT_COINS,
        homepage_preference = "v2"
    )

    print(f"\n  ✅ Utilisateur '{username}' créé avec succès !\n")
    
    return user


def create_session_for_user(user, sessions):

    sessions_str = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sessions_str += "\n  🎮 Sélection des sessions"
    sessions_str += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    sessions_str += "\n  À quelle(s) session(s) cet utilisateur aura accès ?"
    sessions_str += "\n  (Écrivez les chiffres séparés par des virgules)\n"
    
    for i, session in enumerate(sessions, start=1):
        sessions_str += f"\n  [{i}] - {session.session_name}"
    sessions_str += "\n\n  → "

    is_valid_sessions_id = False

    while not is_valid_sessions_id:
        try:
            which_sessions = input(sessions_str)
            which_sessions = which_sessions.split(",")
            which_sessions = [int(session_id.strip()) for session_id in which_sessions]

            if not all(1 <= i <= len(sessions) for i in which_sessions):
                raise ValueError(f"Veuillez écrire des nombres entre 1 et {len(sessions)}.")
            
            if len(which_sessions) != len(set(which_sessions)):
                raise ValueError("Veuillez écrire des nombres strictement différents.")
            
            validation_str = "\n  Vous avez sélectionné les sessions suivantes :\n"
            for session_id in which_sessions:
                validation_str += f"    • {sessions[session_id - 1].session_name}\n"
            validation_str += "\n  Êtes-vous d'accord ?\n  [1] - Oui\n  [2] - Non\n\n  → "

            while True:
                is_sessions_choice_ok = input(validation_str)

                if is_sessions_choice_ok.lower() not in ['1', '2', 'oui', 'non']:
                    print("\n  ⚠️  Commence vraiment pas à essayer de faire le malin...\n")
                else:
                    break
            
            if is_sessions_choice_ok.lower() in ['oui', '1']:
                is_valid_sessions_id = True
                print("\n  ✅ Sessions enregistrées !\n")
            else:
                print("\n  🔄 Alors concentre-toi deux secondes par pitié, t'as combien de QI sérieusement ?\n")

        except ValueError as e:
            print(f"\n  ❌ Format de réponse invalide : {e}\n")


    for session_id in which_sessions:
        session = sessions[int(session_id) - 1]
        SessionUser.objects.create(session=session, user=user)


def generate_quest(user, quest_type : str):

    try:
        # Get quantity of loot (1 for box, random nb for coins)
        quantity = 1
        if quest_type == 'coins':
            quantity = round(rd.normalvariate(mu = 150, sigma = 10))

        # Create quest
        quest = Quest.objects.create(user = user,
                                    loot_type = quest_type,
                                    quantity = quantity,
                                    duration = timedelta(days=1))
        
        
        objectives = rd.sample(list(ObjectifQuest.objects.all()), 3)

        for objective in objectives:
            value = rd.randint(objective.n_min, objective.n_max)
            ObjectifForQuest.objects.create(quest = quest, 
                                            objectif = objective,
                                            objective_value = value)
    except Exception as e:
        raise SystemError(f"Erreur lors de la génération des quêtes : {e}")



@transaction.atomic()
def run():
    
    print("\n╔══════════════════════════════════════╗")
    print("║   🦕 Création d'utilisateur Diplo    ║")
    print("╚══════════════════════════════════════╝\n")

    is_creating_user = input("  Vous souhaitez créer un nouvel utilisateur ?\n  [1] - Oui\n  [2] - Non\n\n  → ")

    while is_creating_user.lower() not in ['1', '2', 'oui', 'non']:
        print("\n  ⚠️  Commence pas à essayer de faire le malin...\n")
        is_creating_user = input("  [1] - Oui\n  [2] - Non\n\n  → ")

    if is_creating_user.lower() in ['2', 'non']:
        print("\n  Alors pourquoi tu sollicites pour rien ?")
        print("  Trouve-toi un travail, j'ai pas que ça à faire moi. Connard va.\n")
        return

    user = create_user()

    sessions = Session.objects.all()
    create_session_for_user(user, sessions)

    # DinoWars
    DWUser.objects.create(
        user=user, 
        free_hatch=DW_FREE_HATCH,
        arena_energy=5
    )

    # Lootboxes
    for _ in range(DEFAULT_BOXES):
        box = Item.objects.create(type='box', item_id=1)
        UserInventory.objects.create(user=user, item=box)

    # Quêtes
    generate_quest(user, quest_type = "coins")
    generate_quest(user, quest_type = "lootbox")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  🎉 Tout est prêt pour '{user.username}' !")
    print(f"     💰 {DEFAULT_COINS} diplodocoins")
    print(f"     📦 {DEFAULT_BOXES} lootboxes")
    print(f"     🦖 Compte DinoWars activé")
    print(f"     📜 Quêtes créées")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")