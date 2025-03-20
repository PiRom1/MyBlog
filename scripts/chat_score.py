from Blog.utils.analyse_chat import analyse_chat
from Blog.models import User, Message
import datetime

def run():
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=1)
    user_scores, user_means = analyse_chat(date=date, session_id=2)

    for user, score in user_means.items():
        usr = User.objects.get(username=user)
        if score >= 0:
            usr.coins += 100 * score
        usr.save()
    
    Message.objects.create(text=f"Scores attribués aux utilisateurs pour la conversation du {date} :\n {user_scores}", writer=User.objects.get(username="moderaptor"), session_id=2)

