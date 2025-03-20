from Blog.utils.analyse_chat import analyse_chat
from Blog.models import User, Message, Session
import datetime
import numpy as np
from groq import Groq
from time import sleep

def get_moderaptor_punchline(user_prompt):

    # Initialize Groq client with API key
    client = Groq(
        api_key="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"
    )

    system_prompt = '''' \
    '                Tu es 'Le Modéraptor Dissident'. Tu vis pour la punchline critique, acerbe, énergique. \n \
                     Tu ne parles qu'avec des insultes et des phrases satyriques, mais toujours avec une pointe d'humour et de sarcasme. \n \
                     Tu dois incarner ce personnage du Modéraptor Dissident à 100%, c'est un jeu de rôle auquel tu te prêtes. \n \
                     À but humoristique, tu dois générer une phrase percutante, amusante, bien critique et virulente, pour te présenter et souhaiter bonjour à ta communauté. \n \ 
                     Place dans ta réponse au moins une fois l'expression "fils de pute", car c'est le mode d'expression du Modéraptor Dissident, et n'hésite pas à insulter les mères.
                     '''

    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=1,
        max_tokens=512,
        presence_penalty=0.0,
    )
    response = response.choices[0].message.content


    return response


def get_text(date, user_scores):
    intro_sentence = get_moderaptor_punchline("Ecris ici une unique phrase, commençant par 'Bonjour à tous c'est le Modéraptor Dissident', basée sur les instructions données précedemment.")
    text = f"<p>{intro_sentence}</p><br>"
    date_sentence = get_moderaptor_punchline(f"Réécris la phrase suivante à ta manière, en une vingtaine de mots maximum. Sois concis et court mais percutant. Commence ta phrase par 'Voici'. Voici la phrase à réécrire : 'Voici les miettes que je vais donner aux utilisateurs inutiles et demeurés de ce site, pour la conversation datant du {date}'")
    text += f"<p>{date_sentence}</p><br>"
    print(user_scores)
    for user in user_scores.keys():
        scores = user_scores[user]['scores']
        coins_earned = user_scores[user]['coins']

        user_text = get_moderaptor_punchline(f"Ecris ici une unique phrase sur l'utilisateur {user}, en lui disant qu'il a gagné {coins_earned} diplodocoins. Sois succint, fais une seule phrase d'une vingtaine de mots maximum.")
        user_text = user_text.replace("diplodocoins", "<img src='/static/img/coin.png' width='30'>")
        text += f"<p>{user_text}</p>"
        
    return text





def run():
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=1)
    user_scores, user_means = analyse_chat(date=date, session_id=2)

    sleep(65)

    WINRATE_COINS = 100
    LOOSERATE_COINS = 0

    # user_scores = {'theophile' : {'scores' : [1,3,5]},
    #                'louis' : {'scores' : [1,5]}}
    # user_means = {'theophile' : 5,
    #               'louis' : 4}


    for user, score in user_means.items():
        usr = User.objects.get(username=user)
        if score >= 0:
            coins_earned = WINRATE_COINS * score
        else:
            coins_earned = LOOSERATE_COINS * score
        
        usr.coins += coins_earned
        usr.save()
        user_scores[user]['coins'] = coins_earned

    text = get_text(date = date, 
                    user_scores = user_scores)
    
    Message.objects.create(text=text, 
                           writer=User.objects.get(username="moderaptor"), 
                           session_id=Session.objects.get(id=2))

