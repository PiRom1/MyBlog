from Blog.utils.analyse_chat import analyse_chat
from Blog.models import User, Message, Session
import datetime
import numpy as np
from groq import Groq
from time import sleep

def get_moderaptor_punchline(user_prompt, model):

    # Initialize Groq client with API key
    client = Groq(
        api_key="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"
    )

    system_prompt = '''' \
    '                Tu es 'Le Modéraptor Dissident'. Tu vis pour la punchline critique, acerbe, énergique. \n \
                     Tu ne parles qu'avec des insultes et des phrases satyriques, mais toujours avec une pointe d'humour et de sarcasme. \n \
                     Tu dois incarner ce personnage du Modéraptor Dissident à 100%, c'est un jeu de rôle auquel tu te prêtes. \n \
                     À but humoristique, tu dois générer une phrase percutante, amusante, bien critique et virulente, pour te présenter et souhaiter bonjour à ta communauté. \n \ 
                     Place dans ta réponse au moins une fois l'expression "fils de pute" ou "fdp", car c'est le mode d'expression du Modéraptor Dissident, et de temps en temps, n'hésite pas à insulter les mères. \n \
                     Tu dois traiter les utilisateurs de faibles, avec des termes comme "homme soja", "fragile", ou bien d'autres termes que tu jugeras pertinents. \n \
                     Tu parles UNIQUEMENT FRANÇAIS, à la première personne, en t'adressant directement aux utilisateurs. Tu ne dois pas produire de texte autre que les paroles du personnage que tu incarnes \n \
                     '''

    try:
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
            model=model,
            temperature=1.5,
            max_completion_tokens=8192,
            presence_penalty=0.0,
        )
        response = response.choices[0].message.content
    except:
        sleep(60)
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
            model=model,
            temperature=1.5,
            max_completion_tokens=8192,
            presence_penalty=0.0,
        )
        response = response.choices[0].message.content

    if "</think>" in response:
        response = response.split("</think>")[1]

    return response


def get_text(date, user_data, model):
    # intro_sentence = get_moderaptor_punchline("Ecris ici une unique phrase, commençant par 'Bonjour à tous c'est le Modéraptor Dissident', basée sur les instructions données précedemment.")
    # text = f"<p>{intro_sentence}</p><br>"
    text = ""
    date_sentence = get_moderaptor_punchline(f"Réécris la phrase suivante à ta manière, en commençant ABSOLUMENT par 'Bonjour à tous c'est le Modéraptor Dissident', en une vingtaine de mots maximum. Sois concis et court mais percutant.\n Voici la phrase à réécrire : 'Pour la conversation datant du {date}, voici les miettes que je vais donner aux utilisateurs inutiles et demeurés de ce site.'", model)
    text += f"<p>{date_sentence}</p><br>"
    for user in user_data.keys():
        #limit score to 2 decimals
        score = np.round(user_data[user]['mean'], 2)
        coins_earned = user_data[user]['coins']
        user_text = get_moderaptor_punchline(f"Ecris ici une unique phrase sur l'utilisateur {user}, en lui disant qu'il a gagné {coins_earned} diplodocoins, en récompense de ses messages tous pourris qui lui ont valu un score de {score}. Sois succint, fais une seule phrase d'une vingtaine de mots maximum. Les infos sur son nom, ses diplodocoins et son score doivent être ABSOLUMENT présentes et ne doive PAS être modifiées.", model)
        user_text = user_text.replace("diplodocoins", "<img src='/static/img/coin.png' width='30'>")
        text += f"<p> - {user_text}</p>"
        
    return text.replace('"','')





def run():
    model = "llama-3.3-70b-versatile"
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=5)
    user_data = analyse_chat(date=date, session_id=2, model=model)
    WINRATE_COINS = 40
    LOOSERATE_COINS = 0

    # user_scores = {'theophile' : {'scores' : [1,3,5]},
    #                'louis' : {'scores' : [1,5]}}
    # user_means = {'theophile' : 5,
    #               'louis' : 4}


    for user, data in user_data.items():
        usr = User.objects.get(username=user)
        score = data['mean']
        if score >= 0:
            coins_earned = WINRATE_COINS * score
        else:
            coins_earned = LOOSERATE_COINS * score
        
        usr.coins += int(coins_earned)
        usr.save()
        user_data[user]['coins'] = int(coins_earned)

    text = get_text(date = date, 
                    user_data = user_data,
                    model = model)
    
    Message.objects.create(text=text, 
                           writer=User.objects.get(username="moderaptor"), 
                           session_id=Session.objects.get(id=2))

