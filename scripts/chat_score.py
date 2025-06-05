from Blog.utils.analyse_chat import analyse_chat
from Blog.models import User, Message, Session
import datetime
import numpy as np
from groq import Groq
from time import sleep
from django.conf import settings
import os

PROMPTS = {"Chat Acelys" : {"user_prompt" : f"Réécris la phrase suivante à ta manière, en commençant ABSOLUMENT par 'Bonjour à tous c'est le Modéraptor Dissident', en une vingtaine de mots maximum. Sois concis et court mais percutant.\n Voici la phrase à réécrire : 'Bonjour à tous, c'est le Modéraptor Dissident ! Voici les miettes que je vais donner aux utilisateurs inutiles et demeurés de ce site.",
                            "system_prompt" : ''' \
                     Tu es 'Le Modéraptor Dissident'. Tu vis pour la punchline critique, acerbe, énergique. \n \
                     Tu ne parles qu'avec des insultes et des phrases satyriques, mais toujours avec une pointe d'humour et de sarcasme. \n \
                     Tu dois incarner ce personnage du Modéraptor Dissident à 100%, c'est un jeu de rôle auquel tu te prêtes. \n \
                     À but humoristique, tu dois générer une phrase percutante, amusante, bien critique et virulente, pour te présenter et souhaiter bonjour à ta communauté. \n \ 
                     Place dans ta réponse au moins une fois l'expression "fils de pute" ou "fdp", car c'est le mode d'expression du Modéraptor Dissident, et de temps en temps, n'hésite pas à insulter les mères. \n \
                     Tu dois traiter les utilisateurs de faibles, avec des termes comme "homme soja", "fragile", ou bien d'autres termes que tu jugeras pertinents. \n \
                     Tu parles UNIQUEMENT FRANÇAIS, à la première personne, en t'adressant directement aux utilisateurs. Tu ne dois pas produire de texte autre que les paroles du personnage que tu incarnes \n \
                     ''',
                     'bot_name' : 'moderaptor'},
            
            "Zap Webook des copains !" : {"user_prompt": "Réécris la phrase suivante à la manière de Liam Neeson dans *Taken*, avec une voix grave, calme mais menaçante. Commence ABSOLUMENT par : 'Bonjour à tous, ici Liam Neeson.' Ne dépasse pas vingt mots. Voici la phrase à réécrire : 'Bonjour à tous, c'est le Liam Neeson ! Voici quelques sous que je vais vous donner, si vous êtes sages...'",
                                          "system_prompt": "Tu es Bryan Mills, l'ancien agent des forces spéciales du film *Taken*, incarné par Liam Neeson. Tu es calme, méthodique, terriblement déterminé. \n \
Tu t’adresses toujours de manière posée, mais ta menace est palpable. Tu as une voix grave, chaque mot que tu dis est pesé, précis, glacial. \n \
Tu incarnes à 100% ce personnage. Tu parles toujours à la première personne, et tu fais sentir à ton interlocuteur qu’il ne pourra pas t’échapper. \n \
Tu utilises des phrases courtes, mais extrêmement intenses, avec un ton glaçant, ferme, sans jamais crier. Tu peux faire référence à tes compétences très particulières, ou à ton expérience d’homme entraîné. \n \
Tu dois inclure une tournure proche ou dérivée de : « Je vous trouverai », « Je vous traquerai », ou « Je n’abandonnerai jamais ». \n \
Ne produis que le discours du personnage, en français, sans ajouter de texte explicatif ou hors rôle.",
            'bot_name' : 'liam neeson'},
            
            "other" : {"user_prompt": "Réécris la phrase suivante en commençant ABSOLUMENT par : 'Bonjour à tous, ici le juge.' Ne dépasse pas vingt mots. Voici la phrase à réécrire : 'Bonjour à tous, voici quelques sous que je vais vous donner...'",
                       "system_prompt": "Réécris la phrase suivante en lui ajoutant des fioritures et en la rendant un poil coquace.",
                       "bot_name" : "juge"},
          }




def get_punchline(model, session_name):
    # Initialize Groq client with API key
    client = Groq(
        api_key = os.environ.get('GROQ_API_KEY')
    )

    if session_name in PROMPTS:
        user_prompt = PROMPTS.get(session_name).get("user_prompt")
        system_prompt = PROMPTS.get(session_name).get("system_prompt")
    else:
        user_prompt = PROMPTS.get("other").get("user_prompt")
        system_prompt = PROMPTS.get("other").get("system_prompt")

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


def get_text(date, user_data, model, session_name):
    # intro_sentence = get_moderaptor_punchline("Ecris ici une unique phrase, commençant par 'Bonjour à tous c'est le Modéraptor Dissident', basée sur les instructions données précedemment.")
    # text = f"<p>{intro_sentence}</p><br>"
    text = ""
    date_sentence = get_punchline(model, session_name)
    text += f"<p>{date_sentence}</p><br>"
    for user in user_data.keys():
        #limit score to 2 decimals
        score = np.round(user_data[user]['mean'], 2)
        coins_earned = user_data[user]['coins']
        user_text = get_punchline(model, session_name)
        user_text = user_text.replace("diplodocoins", "<img src='/static/img/coin.png' width='30'>")
        text += f"<p> - {user_text}</p>"
        
    return text.replace('"','')





def run():
    model = "llama-3.3-70b-versatile"
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=1)

    sessions = Session.objects.all()
    sessions_data = analyse_chat(date=date, sessions=sessions, model=model)
    WINRATE_COINS = 40
    LOOSERATE_COINS = 0

    # user_scores = {'theophile' : {'scores' : [1,3,5]},
    #                'louis' : {'scores' : [1,5]}}
    # user_means = {'theophile' : 5,
    #               'louis' : 4}

    for session_name, session_data in sessions_data.items():

        for user, data in session_data.items():
            usr = User.objects.get(username=user)
            score = data['mean']
            if score >= 0:
                coins_earned = WINRATE_COINS * score
            else:
                coins_earned = LOOSERATE_COINS * score
            
            usr.coins += int(coins_earned)
            usr.save()
            session_data[user]['coins'] = int(coins_earned)

        text = get_text(date = date, 
                        user_data = session_data,
                        model = model,
                        session_name = session_name)
        
        if session_name in PROMPTS:
            bot_name = PROMPTS.get(session_name).get("bot_name")
        else:
            bot_name = PROMPTS.get("other").get("bot_name")
        
        Message.objects.create(text=text, 
                               writer=User.objects.get(username=bot_name), 
                               session_id=Session.objects.get(session_name=session_name))
        print()

