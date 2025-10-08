import datetime
from time import sleep
from Blog.models import User, Message, Bot, Session
from groq import Groq
from django.conf import settings
import os
import numpy as np


"""
Scripts to analyze chat and attribute scores to each users according to the contribution to each chat.
"""


## PARAMETERS



PROMPTS = {"Chat Acelys" : {"intro_prompt" : f"Réécris la phrase suivante à ta manière, en commençant ABSOLUMENT par 'Bonjour à tous c'est le Modéraptor Dissident', en une vingtaine de mots maximum. Sois concis et court mais percutant.\n Voici la phrase à réécrire : 'Bonjour à tous, c'est le Modéraptor Dissident ! Voici les miettes que je vais donner aux utilisateurs inutiles et demeurés de ce site.",
                            "reward_prompt" : "Ecris ici une unique phrase sur l'utilisateur --USER, en lui disant qu'il a gagné --COINS diplodocoins, en récompense de ses messages tous pourris qui lui ont valu un score de --SCORE. Sois succint, fais une seule phrase d'une vingtaine de mots maximum. Les infos sur son nom, ses diplodocoins et son score doivent être ABSOLUMENT présentes et ne doive PAS être modifiées.",
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
            
            "Zap Webook des copains !" : {"intro_prompt": "Réécris la phrase suivante à la manière de Liam Neeson dans *Taken*, avec une voix grave, calme mais menaçante. Commence ABSOLUMENT par : 'Bonjour à tous, ici Liam Neeson.' Ne dépasse pas vingt mots. Voici la phrase à réécrire : 'Bonjour à tous, c'est le Liam Neeson ! Voici quelques sous que je vais vous donner, si vous êtes sages...'",
                                          "reward_prompt" : "Ecris ici une unique phrase sur l'utilisateur --USER, en lui disant qu'il a gagné --COINS diplodocoins, en récompense de ses messages tous pourris qui lui ont valu un score de --SCORE. Sois succint, fais une seule phrase d'une vingtaine de mots maximum. Les infos sur son nom, ses diplodocoins et son score doivent être ABSOLUMENT présentes et ne doive PAS être modifiées.",
                                          "system_prompt": "Tu es Bryan Mills, l'ancien agent des forces spéciales du film *Taken*, incarné par Liam Neeson. Tu es calme, méthodique, terriblement déterminé. \n \
Tu t’adresses toujours de manière posée, mais ta menace est palpable. Tu as une voix grave, chaque mot que tu dis est pesé, précis, glacial. \n \
Tu incarnes à 100% ce personnage. Tu parles toujours à la première personne, et tu fais sentir à ton interlocuteur qu’il ne pourra pas t’échapper. \n \
Tu utilises des phrases courtes, mais extrêmement intenses, avec un ton glaçant, ferme, sans jamais crier. Tu peux faire référence à tes compétences très particulières, ou à ton expérience d’homme entraîné. \n \
Tu dois inclure une tournure proche ou dérivée de : « Je vous trouverai », « Je vous traquerai », ou « Je n’abandonnerai jamais ». \n \
Ne produis que le discours du personnage, en français, sans ajouter de texte explicatif ou hors rôle.",
            'bot_name' : 'liam_neeson'},
            
            "other" : {"intro_prompt": "Réécris la phrase suivante en commençant ABSOLUMENT par : 'Bonjour à tous, ici le juge.' Ne dépasse pas vingt mots. Voici la phrase à réécrire : 'Bonjour à tous, voici quelques sous que je vais vous donner...'",
                       "reward_prompt" : "Ecris ici une unique phrase sur l'utilisateur --USER, en lui disant qu'il a gagné --COINS diplodocoins, en récompense de ses messages tous pourris qui lui ont valu un score de --SCORE. Sois succint, fais une seule phrase d'une vingtaine de mots maximum. Les infos sur son nom, ses diplodocoins et son score doivent être ABSOLUMENT présentes et ne doive PAS être modifiées.",
                       "system_prompt": "Réécris la phrase suivante en lui ajoutant des fioritures et en la rendant un poil coquace.",
                       "bot_name" : "juge"},
          }


## FUNCTIONS

def analyse_chat(sessions, date=datetime.date.today(), model="mixtral-8x7b-32768"):
    
    # Get all the messages of the day, for the sessions given

    bot_users = Bot.objects.all().values_list('user', flat = True)
    sessions_data = {}

    for session in sessions:
        print(f"Notation pour la session {session.session_name}")

        messages = Message.objects.filter(pub_date__date=date, session_id=session.id).exclude(writer__in=bot_users)
       
        if messages.count() == 0 or messages.exclude(writer__in=bot_users).count() == 0:
            print(f"Pas de messages récents à noter pour la session {session.session_name}")
            continue

        # Get all the users who sent a message today
        users = []
        for message in messages:
            if message.writer not in users and message.writer.username != "moderaptor":
                users.append(message.writer.username)

        messages_batch = [""]
        i = 0
        count = 0
        curr_batch_size = 0
        while i < len(messages):
            # Remove html tags from the message : replace any text between < and > by a space
            msg_text = messages[i].text
            while "<" in msg_text:
                start = msg_text.find("<")
                end = msg_text.find(">")
                msg_text = msg_text[:start] + " " + msg_text[end+1:]
            if msg_text == "":
                i += 1
                pass
            count += len(msg_text.split()) * 1.5
            if count < 4500:
                messages_batch[-1] += "USER : "+ messages[i].writer.username + "\nMESSAGE : '''" + msg_text + "'''\n\n"
                i += 1
                curr_batch_size += 1
            else:
                if curr_batch_size < 3:
                    raise Exception("A message is too long to be analysed.")
                messages_batch.append("")
                count = 0
                curr_batch_size = 0
                print("Break at message " + str(i))
                i -= 2
                
        # For each user, analyse the contribution to the conversation
        # Use groq to analyse the conversation, and give a score to the user
        # The score is based on the relevance of the user's messages to the conversation, the amount of reactions to the user's messages, and the amount of content the user has brought to the conversation.
        # The score is independent of the user's identity, and is only based on the user's contribution to the conversation.
        # The score is independent of the positive or negative nature of the user's messages, and is only based on how the user's messages bring reactions and content to the conversation.

        system_prompt = "You are a classifying system that analyses conversations and gives scores to multiple users based on their relevance to the conversation, reactions to their messages, and content contribution." \
        "The scores are INDEPENDENT of the positive or negative nature of messages, and only based on how users' messages BRING REACTION and NEW CONTENT." \
        "Scores are between -5 and 10, with -5 being irrelevant and conversation-killing, 0 being neutral, and 10 being very relevant and conversation-enhancing."

        prompt = "Analyse the following conversation and give a score to EACH message based on:" \
        "\n- Amount of reactions to their messages" \
        "\n- Amount of new content brought to the conversation" \
        "\nScores should be independent of the positive/negative nature of messages." \
        "\nDO NOT penalize users for negative messages, only for contentless and spam messages." \
        "\nNegative content should be scored based on the amount of reactions and content it brings. It may score high if it brings a lot of reactions and content." \
        "\nReward content-rich messages and messages that bring reactions, more than responses" \
        "\nTemper your scores on responses messages. In general, 8,9,10 should be extraordinary messages, 5,6,7 should be good messages, 2,3,4 should be average messages, and 0,1 should be ok messages. Negatives are for Spam content, killing-chat messages." \
        "\nDo not focus only on the first subject of the conversation, as it way evolve." \
        "\nProvide score for EACH MESSAGE of each user in the format: USERNAME: SCORE - BRIEF_REASON" \
        "\nDo not repeat the messages in the conversation, only the scores." \
        "\nThe conversation is as follows:"

        prompt_end = "Complete the following dictionary with the scores for each user :\n"

        user_dict = "{"
        for user in users:
            user_dict += user + ": SCORE - BRIEF_REASON\n"
        user_dict += "}\n"
        "OUTPUT ONLY THE DICTIONARY, NOTHING ELSE"
        
        # Initialize Groq client with API key
        client = Groq(
            api_key = os.environ.get('GROQ_API_KEY')
        )
        responses = []
        for i, messages_string in enumerate(messages_batch):
            print('Batch ' + str(i+1) + ' out of ' + str(len(messages_batch)))
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt + "\n\n" + messages_string + "\n\n" + prompt_end + user_dict
                    }
                ],
                model=model,
                temperature=0,
                max_completion_tokens=8192,
                presence_penalty=0.0,
            )
            response = response.choices[0].message.content
            if "</think>" in response:
                response = response.split("</think>")[1]
            
            print(response)
        
            if "{" in response:
                response = response.split("{")[1].split("}")[0]
            responses.append(response)
            if i < len(messages_batch)-1:
                sleep(60)

        response = "\n".join(responses)
        user_scores = {}
        for user in users:
            user_scores[user] = []
            for line in response.split("\n"):
                if user+":" in line:
                    score = line.split(user+": ")[1][0:2].strip()
                    user_scores[user].append(score)
    
        user_means = {}
        for user in user_scores:
            user_means[user] = sum([int(score) for score in user_scores[user]])/(len(user_scores[user])+2.5)
            print(user + " : " + str(sum([int(score) for score in user_scores[user]])/(len(user_scores[user])+2.5)))

        user_data = {}
        for user in users:
            user_data[user] = {}
            user_data[user]["scores"] = user_scores[user]
            user_data[user]["mean"] = user_means[user]
        
        sessions_data[session.session_name] = user_data
    
    return sessions_data





def get_punchline(user_prompt, model, session_name):
    """
    Get the punchline of the bot that gives scores and coins
    """

    # Initialize Groq client with API key
    client = Groq(
        api_key = os.environ.get('GROQ_API_KEY')
    )

    if session_name in PROMPTS:
        system_prompt = PROMPTS.get(session_name).get("system_prompt")
    else:
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
    """
    Get the text of the bot that gives notes and coins.
    """
   

    # get prompt
    if session_name in PROMPTS:
        intro_prompt = PROMPTS.get(session_name).get("intro_prompt")
        reward_prompt = PROMPTS.get(session_name).get("reward_prompt")
    else:
        intro_prompt = PROMPTS.get("other").get("intro_prompt")
        reward_prompt = PROMPTS.get("other").get("reward_prompt")

    text = ""
    date_sentence = get_punchline(intro_prompt, model, session_name)
    text += f"<p>{date_sentence}</p><br>"
    for user in user_data.keys():
        user_reward_prompt = reward_prompt
        user_reward_prompt = user_reward_prompt.replace('--USER', user)
        user_reward_prompt = user_reward_prompt.replace('--COINS', str(user_data.get(user).get('coins')))
        user_reward_prompt = user_reward_prompt.replace('--SCORE', str(round(user_data.get(user).get('mean'), 2)))

        #limit score to 2 decimals
        score = np.round(user_data[user]['mean'], 2)
        coins_earned = user_data[user]['coins']
        user_text = get_punchline(user_reward_prompt, model, session_name)
        user_text = user_text.replace("diplodocoins", "<img src='/static/img/coin.png' width='30'>")
        text += f"<p> - {user_text}</p>"
        
    return text.replace('"','')





def chat_score():
    """
    Attribute a note and coins to each users of each sessions. Use every scribts above.
    """
    
    print("Initialisation chat score ...")

    model = "llama-3.3-70b-versatile"
    # Date of yesterday
    date = datetime.date.today() - datetime.timedelta(days=1)

    sessions = Session.objects.all()
    sessions_data = analyse_chat(date=date, sessions=sessions, model=model)
    print("Session data récupérée")

    if not sessions_data:
        print("Pas de donées récentes à analyser")
        return
    
    WINRATE_COINS = 40
    LOOSERATE_COINS = 0

    # user_scores = {'theophile' : {'scores' : [1,3,5]},
    #                'louis' : {'scores' : [1,5]}}
    # user_means = {'theophile' : 5,
    #               'louis' : 4}

    for session_name, session_data in sessions_data.items():

        if not session_data:
            print(f"Pas de messages envoyés pour la session {session_name}")
            continue

        print(f"Analyzing session {session_name}")

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
        print("text récuperé")
        
        if session_name in PROMPTS:
            bot_name = PROMPTS.get(session_name).get("bot_name")
        else:
            bot_name = PROMPTS.get("other").get("bot_name")
        
        Message.objects.create(text=text, 
                               writer=User.objects.get(username=bot_name), 
                               session_id=Session.objects.get(session_name=session_name))
        print()



    

