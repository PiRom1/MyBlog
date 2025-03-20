import datetime
from Blog.models import User, Message, Bot
from groq import Groq

def analyse_chat(date=datetime.date.today(), session_id=2):
    # Get all the messages of the day, for the session id 2

    # bot_users = Bot.objects.all().values_list('user', flat = True)

    messages = Message.objects.filter(pub_date__date=date, session_id=session_id)#.exclude(writer__in=bot_users)

    # Get all the users who sent a message today
    users = []
    for message in messages:
        if message.writer not in users:
            users.append(message.writer.username)

    messages_string = ""
    for message in messages:
        messages_string += "USER : "+ message.writer.username + "\nMESSAGE : '''" + message.text + "'''\n\n"

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
    "\nDo not focus only on the first subject of the conversation, as it way evolve." \
    "\nProvide score for EACH MESSAGE of each user in the format: USERNAME: SCORE - BRIEF_REASON" \
    "\nDo not repeat the messages in the conversation, only the scores." \
    "\nThe conversation is as follows:"

    prompt_end = "Complete the following dictionary with the scores for each user :\n"

    user_dict = "{"
    for user in users:
        user_dict += user + ": SCORE - BRIEF_REASON\n"
    user_dict += "}"
    
    # Initialize Groq client with API key
    client = Groq(
        api_key="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"
    )

    
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
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=512,
        presence_penalty=0.0,
    )
    response = response.choices[0].message.content
    print(response)
    
    user_scores = {}
    for user in users:
        user_scores[user] = {'scores' : []}
        for line in response.split("\n"):
            if user+":" in line:
                score = line.split(user+": ")[1][0:2].strip()
                user_scores[user]['scores'].append(int(score))
    print(user_scores)
    user_means = {}
    for user in user_scores:
        user_means[user] = sum([score for score in user_scores[user]['scores']])/len(user_scores[user]['scores'])
        print(user + " : " + str(sum([score for score in user_scores[user]['scores']])/len(user_scores[user]['scores'])))
    
    return user_scores, user_means

    

