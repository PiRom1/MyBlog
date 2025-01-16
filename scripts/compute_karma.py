from Blog.models import Message
from Blog.views.karma_views import *
import time

def run():

    debut = time.time()    
    messages = Message.objects.all()
    analyse_sentiment_macro(messages, spam_threshold=5)
    fin = time.time()

    print(f"Karma calculé sur l'ensemble des messages. Temps d'éxecution : {fin - debut} secondes. Temps moyen par message : {(fin - debut) / len(messages)}.")
    

