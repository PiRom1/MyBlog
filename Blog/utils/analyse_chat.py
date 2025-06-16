import datetime
from time import sleep
from Blog.models import User, Message, Bot
from groq import Groq
from django.conf import settings
import os

def analyse_chat(sessions, date=datetime.date.today(), model="mixtral-8x7b-32768"):
    # Get all the messages of the day, for the session id 2

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

    

