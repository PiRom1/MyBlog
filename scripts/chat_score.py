from Blog.utils.analyse_chat import analyse_chat
from Blog.models import User, Message, Session
import datetime

def run():
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=1)
    user_scores, user_means = analyse_chat(date=date, session_id=2)

    WINRATE_COINS = 100
    LOOSERATE_COINS = 0

    user_coins = {}

    for user, score in user_means.items():
        usr = User.objects.get(username=user)
        if score >= 0:
            coins_earned = WINRATE_COINS * score
        else:
            coins_earned = LOOSERATE_COINS * score
        
        usr.coins += coins_earned
        usr.save()

        user_coins[user] = coins_earned
    
    Message.objects.create(text=f"Scores attribués aux utilisateurs pour la conversation du {date} :\n {user_scores}. \n \
                           Pièces gagnées : {user_coins}.", 
                           writer=User.objects.get(username="moderaptor"), 
                           session_id=Session.objects.get(id=2))

